from __future__ import annotations

import asyncio
import re
from functools import partial
from itertools import starmap
from pathlib import Path, PurePath
from typing import Callable, Iterable, Optional
from urllib.parse import unquote

from markdown_it import MarkdownIt
from markdown_it.token import Token
from rich.text import Text
from typing_extensions import TypeAlias

from textual._slug import TrackedSlugs, slug
from textual.app import ComposeResult
from textual.await_complete import AwaitComplete
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.content import Content
from textual.css.query import NoMatches
from textual.events import Mount
from textual.highlight import highlight
from textual.layout import Layout
from textual.layouts.grid import GridLayout
from textual.message import Message
from textual.reactive import reactive, var
from textual.style import Style
from textual.widget import Widget
from textual.widgets import Static, Tree

TableOfContentsType: TypeAlias = "list[tuple[int, str, str | None]]"
"""Information about the table of contents of a markdown document.

The triples encode the level, the label, and the optional block id of each heading.
"""


class MarkdownStream:
    """An object to manager streaming markdown.

    This will accumulate markdown fragments if they can't be rendered fast enough.

    This object is typically created by the [Markdown.get_stream][textual.widgets.Markdown.get_stream] method.

    """

    def __init__(self, markdown_widget: Markdown) -> None:
        """
        Args:
            markdown_widget: Markdown widget to update.
        """
        self.markdown_widget = markdown_widget
        self._task: asyncio.Task | None = None
        self._new_markup = asyncio.Event()
        self._pending: list[str] = []
        self._stopped = False

    def start(self) -> None:
        """Start the updater running in the background.

        No need to call this, if the object was created by [Markdown.get_stream][textual.widgets.Markdown.get_stream].

        """
        if self._task is None:
            self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        """Stop the stream and await its finish."""
        if self._task is not None:
            self._task.cancel()
            await self._task
            self._task = None
            self._stopped = True

    async def write(self, markdown_fragment: str) -> None:
        """Append or enqueue a markdown fragment.

        Args:
            markdown_fragment: A string to append at the end of the document.
        """
        if self._stopped:
            raise RuntimeError("Can't write to the stream after it has stopped.")
        if not markdown_fragment:
            # Nothing to do for empty strings.
            return
        # Append the new fragment, and set an event to tell the _run loop to wake up
        self._pending.append(markdown_fragment)
        self._new_markup.set()

    async def _run(self) -> None:
        """Run a task to append markdown fragments when available."""
        try:
            while await self._new_markup.wait():
                new_markdown = "".join(self._pending)
                self._pending.clear()
                self._new_markup.clear()
                await asyncio.shield(self.markdown_widget.append(new_markdown))
        except asyncio.CancelledError:
            # Task has been cancelled, add any outstanding markdown
            new_markdown = "".join(self._pending)
            if new_markdown:
                await self.markdown_widget.append(new_markdown)


class Navigator:
    """Manages a stack of paths like a browser."""

    def __init__(self) -> None:
        self.stack: list[Path] = []
        self.index = 0

    @property
    def location(self) -> Path:
        """The current location.

        Returns:
            A path for the current document.
        """
        if not self.stack:
            return Path(".")
        return self.stack[self.index]

    @property
    def start(self) -> bool:
        """Is the current location at the start of the stack?"""
        return self.index == 0

    @property
    def end(self) -> bool:
        """Is the current location at the end of the stack?"""
        return self.index >= len(self.stack) - 1

    def go(self, path: str | PurePath) -> Path:
        """Go to a new document.

        Args:
            path: Path to new document.

        Returns:
            New location.
        """
        location, anchor = Markdown.sanitize_location(str(path))
        if location == Path(".") and anchor:
            current_file, _ = Markdown.sanitize_location(str(self.location))
            path = f"{current_file}#{anchor}"
        new_path = self.location.parent / Path(path)
        self.stack = self.stack[: self.index + 1]
        new_path = new_path.absolute()
        self.stack.append(new_path)
        self.index = len(self.stack) - 1
        return new_path

    def back(self) -> bool:
        """Go back in the stack.

        Returns:
            True if the location changed, otherwise False.
        """
        if self.index:
            self.index -= 1
            return True
        return False

    def forward(self) -> bool:
        """Go forward in the stack.

        Returns:
            True if the location changed, otherwise False.
        """
        if self.index < len(self.stack) - 1:
            self.index += 1
            return True
        return False


class MarkdownBlock(Static):
    """The base class for a Markdown Element."""

    DEFAULT_CSS = """
    MarkdownBlock {
        width: 1fr;
        height: auto;
    }
    """

    def __init__(self, markdown: Markdown, *args, **kwargs) -> None:
        self._markdown: Markdown = markdown
        """A reference to the Markdown document that contains this block."""
        self._content: Content = Content()
        self._token: Token | None = None
        self._blocks: list[MarkdownBlock] = []
        super().__init__(*args, **kwargs)

    @property
    def select_container(self) -> Widget:
        return self.query_ancestor(Markdown)

    def compose(self) -> ComposeResult:
        yield from self._blocks
        self._blocks.clear()

    def set_content(self, content: Content) -> None:
        self._content = content
        self.update(content)

    async def _update_from_block(self, block: MarkdownBlock) -> None:
        await self.remove()
        await self._markdown.mount(block)

    async def action_link(self, href: str) -> None:
        """Called on link click."""
        self.post_message(Markdown.LinkClicked(self._markdown, href))

    def notify_style_update(self) -> None:
        """If CSS was reloaded, try to rebuild this block from its token."""
        super().notify_style_update()
        self.rebuild()

    def rebuild(self) -> None:
        """Rebuild the content of the block if we have a source token."""
        if self._token is not None:
            self.build_from_token(self._token)

    def build_from_token(self, token: Token) -> None:
        """Build the block content from its source token.

        This method allows the block to be rebuilt on demand, which is useful
        when the styles assigned to the
        [Markdown.COMPONENT_CLASSES][textual.widgets.Markdown.COMPONENT_CLASSES]
        change.

        See https://github.com/Textualize/textual/issues/3464 for more information.

        Args:
            token: The token from which this block is built.
        """

        self._token = token
        null_style = Style.null()
        style_stack: list[Style] = [Style()]
        pending_content: list[tuple[str, Style]] = []

        def add_content(text: str, style: Style) -> None:
            """Add text and style to output content.

            Args:
                text: String of content.
                style: Style of string.
            """
            if pending_content:
                top_text, top_style = pending_content[-1]
                if top_style == style:
                    pending_content[-1] = (top_text + text, style)
                else:
                    pending_content.append((text, style))
            else:
                pending_content.append((text, style))

        get_visual_style = self._markdown.get_visual_style
        if token.children is None:
            self.set_content(Content(""))
            return
        for child in token.children:
            child_type = child.type
            if child_type == "text":
                add_content(re.sub(r"\s+", " ", child.content), style_stack[-1])
            if child_type == "hardbreak":
                add_content("\n", null_style)
            if child_type == "softbreak":
                add_content(" ", style_stack[-1])
            elif child_type == "code_inline":
                add_content(
                    child.content,
                    style_stack[-1] + get_visual_style("code_inline"),
                )
            elif child_type == "em_open":
                style_stack.append(
                    style_stack[-1] + get_visual_style("em", partial=True)
                )
            elif child_type == "strong_open":
                style_stack.append(
                    style_stack[-1] + get_visual_style("strong", partial=True)
                )
            elif child_type == "s_open":
                style_stack.append(
                    style_stack[-1] + get_visual_style("s", partial=True)
                )
            elif child_type == "link_open":
                href = child.attrs.get("href", "")
                action = f"link({href!r})"
                style_stack.append(
                    style_stack[-1] + Style.from_meta({"@click": action})
                )
            elif child_type == "image":
                href = child.attrs.get("src", "")
                alt = child.attrs.get("alt", "")
                action = f"link({href!r})"
                style_stack.append(
                    style_stack[-1] + Style.from_meta({"@click": action})
                )
                add_content("🖼  ", style_stack[-1])
                if alt:
                    add_content(f"({alt})", style_stack[-1])
                if child.children is not None:
                    for grandchild in child.children:
                        add_content(grandchild.content, style_stack[-1])
                style_stack.pop()

            elif child_type.endswith("_close"):
                style_stack.pop()

        content = Content("").join(starmap(Content.styled, pending_content))
        self.set_content(content)


class MarkdownHeader(MarkdownBlock):
    """Base class for a Markdown header."""

    DEFAULT_CSS = """
    MarkdownHeader {
        color: $text;
        margin: 2 0 1 0;

    }
    """


class MarkdownH1(MarkdownHeader):
    """An H1 Markdown header."""

    DEFAULT_CSS = """
    MarkdownH1 {
        content-align: center middle;
        color: $markdown-h1-color;
        background: $markdown-h1-background;
        text-style: $markdown-h1-text-style;
    }
    """


class MarkdownH2(MarkdownHeader):
    """An H2 Markdown header."""

    DEFAULT_CSS = """
    MarkdownH2 {
        color: $markdown-h2-color;
        background: $markdown-h2-background;
        text-style: $markdown-h2-text-style;
    }
    """


class MarkdownH3(MarkdownHeader):
    """An H3 Markdown header."""

    DEFAULT_CSS = """
    MarkdownH3 {
        color: $markdown-h3-color;
        background: $markdown-h3-background;
        text-style: $markdown-h3-text-style;
        margin: 1 0;
        width: auto;
    }
    """


class MarkdownH4(MarkdownHeader):
    """An H4 Markdown header."""

    DEFAULT_CSS = """
    MarkdownH4 {
        color: $markdown-h4-color;
        background: $markdown-h4-background;
        text-style: $markdown-h4-text-style;
        margin: 1 0;
    }
    """


class MarkdownH5(MarkdownHeader):
    """An H5 Markdown header."""

    DEFAULT_CSS = """
    MarkdownH5 {
        color: $markdown-h5-color;
        background: $markdown-h5-background;
        text-style: $markdown-h5-text-style;
        margin: 1 0;
    }
    """


class MarkdownH6(MarkdownHeader):
    """An H6 Markdown header."""

    DEFAULT_CSS = """
    MarkdownH6 {
        color: $markdown-h6-color;
        background: $markdown-h6-background;
        text-style: $markdown-h6-text-style;
        margin: 1 0;
    }
    """


class MarkdownHorizontalRule(MarkdownBlock):
    """A horizontal rule."""

    DEFAULT_CSS = """
    MarkdownHorizontalRule {
        border-bottom: solid $secondary;
        height: 1;
        padding-top: 1;
        margin-bottom: 1;
    }
    """


class MarkdownParagraph(MarkdownBlock):
    """A paragraph Markdown block."""

    SCOPED_CSS = False
    DEFAULT_CSS = """
    Markdown > MarkdownParagraph {
         margin: 0 0 1 0;
    }
    """


class MarkdownBlockQuote(MarkdownBlock):
    """A block quote Markdown block."""

    DEFAULT_CSS = """
    MarkdownBlockQuote {
        background: $boost;
        border-left: outer $primary 50%;
        margin: 1 0;
        padding: 0 1;
    }
    MarkdownBlockQuote:light {
        border-left: outer $secondary;
    }
    MarkdownBlockQuote > BlockQuote {
        margin-left: 2;
        margin-top: 1;
    }
    """


class MarkdownList(MarkdownBlock):
    DEFAULT_CSS = """

    MarkdownList {
        width: 1fr;
    }

    MarkdownList MarkdownList {
        margin: 0;
        padding-top: 0;
    }
    """


class MarkdownBulletList(MarkdownList):
    """A Bullet list Markdown block."""

    DEFAULT_CSS = """
    MarkdownBulletList {
        margin: 0 0 1 0;
        padding: 0 0;
    }

    MarkdownBulletList Horizontal {
        height: auto;
        width: 1fr;
    }

    MarkdownBulletList Vertical {
        height: auto;
        width: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        for block in self._blocks:
            if isinstance(block, MarkdownListItem):
                bullet = MarkdownBullet()
                bullet.symbol = block.bullet
                yield Horizontal(bullet, Vertical(*block._blocks))
        self._blocks.clear()


class MarkdownOrderedList(MarkdownList):
    """An ordered list Markdown block."""

    DEFAULT_CSS = """
    MarkdownOrderedList {
        margin: 0 0 1 0;
        padding: 0 0;
    }

    MarkdownOrderedList Horizontal {
        height: auto;
        width: 1fr;
    }

    MarkdownOrderedList Vertical {
        height: auto;
        width: 1fr;        
    }
    """

    def compose(self) -> ComposeResult:
        suffix = ". "
        start = 1
        if self._blocks and isinstance(self._blocks[0], MarkdownOrderedListItem):
            try:
                start = int(self._blocks[0].bullet)
            except ValueError:
                pass
        symbol_size = max(
            len(f"{number}{suffix}")
            for number, block in enumerate(self._blocks, start)
            if isinstance(block, MarkdownListItem)
        )
        for number, block in enumerate(self._blocks, start):
            if isinstance(block, MarkdownListItem):
                bullet = MarkdownBullet()
                bullet.symbol = f"{number}{suffix}".rjust(symbol_size + 1)
                yield Horizontal(bullet, Vertical(*block._blocks))

        self._blocks.clear()


class MarkdownTableCellContents(Static):
    """Widget for table cells.

    A shim over a Static which responds to links.
    """

    async def action_link(self, href: str) -> None:
        """Pass a link action on to the MarkdownTable parent."""
        self.post_message(Markdown.LinkClicked(self.query_ancestor(Markdown), href))


class MarkdownTableContent(Widget):
    """Renders a Markdown table."""

    DEFAULT_CSS = """
    MarkdownTableContent {
        width: 1fr;        
        height: auto;
        layout: grid;        
        grid-columns: auto;   
        grid-rows: auto;    
        grid-gutter: 1 1; 
                
        & > .cell {
            margin: 0 0;
            height: auto;
            padding: 0 1;
            text-overflow: ellipsis;
            
        }
        & > .header {
            height: auto;
            margin: 0 0;
            padding: 0 1;
            color: $primary;
            text-overflow: ellipsis;            
            content-align: left bottom;            
        }
        keyline: thin $foreground 20%;                
    }
    MarkdownTableContent > .markdown-table--header {
        text-style: bold;
    }
    """

    COMPONENT_CLASSES = {"markdown-table--header", "markdown-table--lines"}

    def __init__(self, headers: list[Content], rows: list[list[Content]]):
        self.headers = headers.copy()
        """List of header text."""
        self.rows = rows.copy()
        """The row contents."""
        super().__init__()
        self.shrink = True
        self.last_row = 0

    def pre_layout(self, layout: Layout) -> None:
        assert isinstance(layout, GridLayout)
        layout.auto_minimum = True
        layout.expand = True
        layout.shrink = True
        layout.stretch_height = True

    def compose(self) -> ComposeResult:
        for header in self.headers:
            yield MarkdownTableCellContents(header, classes="header").with_tooltip(
                header
            )
        for row_index, row in enumerate(self.rows, 1):
            for cell in row:
                yield MarkdownTableCellContents(
                    cell, classes=f"row{row_index} cell"
                ).with_tooltip(cell.plain)
            self.last_row = row_index

    async def _update_rows(self, updated_rows: list[list[Content]]) -> None:
        self.styles.grid_size_columns = len(self.headers)
        await self.query_children(f".cell.row{self.last_row}").remove()
        new_cells: list[Static] = []
        for row_index, row in enumerate(updated_rows, self.last_row):
            for cell in row:
                new_cells.append(
                    Static(cell, classes=f"row{row_index} cell").with_tooltip(cell)
                )
        self.last_row = row_index
        await self.mount_all(new_cells)

    def on_mount(self) -> None:
        self.styles.grid_size_columns = len(self.headers)

    async def action_link(self, href: str) -> None:
        """Pass a link action on to the MarkdownTable parent."""
        if isinstance(self.parent, MarkdownTable):
            await self.parent.action_link(href)


class MarkdownTable(MarkdownBlock):
    """A Table markdown Block."""

    DEFAULT_CSS = """
    MarkdownTable {
        width: 1fr;      
        margin-bottom: 1;      
        &:light {
            background: white 30%;
        }        
    }
    """

    def __init__(self, markdown: Markdown, *args, **kwargs) -> None:
        super().__init__(markdown, *args, **kwargs)
        self._headers: list[Content] = []
        self._rows: list[list[Content]] = []

    def compose(self) -> ComposeResult:
        headers, rows = self._get_headers_and_rows()
        self._headers = headers
        self._rows = rows
        yield MarkdownTableContent(headers, rows)

    def _get_headers_and_rows(self) -> tuple[list[Content], list[list[Content]]]:
        """Get list of headers, and list of rows.

        Returns:
            A tuple containing a list of headers, and a list of rows.
        """

        def flatten(block: MarkdownBlock) -> Iterable[MarkdownBlock]:
            for block in block._blocks:
                if block._blocks:
                    yield from flatten(block)
                yield block

        headers: list[Content] = []
        rows: list[list[Content]] = []
        for block in flatten(self):
            if isinstance(block, MarkdownTH):
                headers.append(block._content)
            elif isinstance(block, MarkdownTR):
                rows.append([])
            elif isinstance(block, MarkdownTD):
                rows[-1].append(block._content)
        if rows and not rows[-1]:
            rows.pop()
        return headers, rows

    async def _update_from_block(self, block: MarkdownBlock) -> None:
        """Special case to update a Markdown table.

        Args:
            block: Existing markdown block.
        """
        if isinstance(block, MarkdownTable):
            try:
                table_content = self.query_one(MarkdownTableContent)
            except NoMatches:
                pass
            else:
                if table_content.rows:
                    current_rows = self._rows
                    _new_headers, new_rows = block._get_headers_and_rows()
                    updated_rows = new_rows[len(current_rows) - 1 :]
                    self._rows = new_rows
                    await table_content._update_rows(updated_rows)
                    return
        await super()._update_from_block(block)


class MarkdownTBody(MarkdownBlock):
    """A table body Markdown block."""


class MarkdownTHead(MarkdownBlock):
    """A table head Markdown block."""


class MarkdownTR(MarkdownBlock):
    """A table row Markdown block."""


class MarkdownTH(MarkdownBlock):
    """A table header Markdown block."""


class MarkdownTD(MarkdownBlock):
    """A table data Markdown block."""


class MarkdownBullet(Widget):
    """A bullet widget."""

    DEFAULT_CSS = """
    MarkdownBullet {
        width: auto;
        color: $text;
        text-style: bold;
        &:light {
            color: $secondary;
        }
    }
    """

    symbol = reactive("\u25cf")
    """The symbol for the bullet."""

    def get_selection(self, _selection) -> tuple[str, str] | None:
        return self.symbol, " "

    def render(self) -> Content:
        return Content(self.symbol)


class MarkdownListItem(MarkdownBlock):
    """A list item Markdown block."""

    DEFAULT_CSS = """
    MarkdownListItem {
        layout: horizontal;
        margin-right: 1;
        height: auto;
    }

    MarkdownListItem > Vertical {
        width: 1fr;
        height: auto;
    }
    """

    def __init__(self, markdown: Markdown, bullet: str) -> None:
        self.bullet = bullet
        super().__init__(markdown)


class MarkdownOrderedListItem(MarkdownListItem):
    pass


class MarkdownUnorderedListItem(MarkdownListItem):
    pass


class MarkdownFence(MarkdownBlock):
    """A fence Markdown block."""

    DEFAULT_CSS = """
    MarkdownFence {
        padding: 1 2;
        margin: 1 0;
        overflow: hidden;
        width: 1fr;
        height: auto;        
        color: rgb(210,210,210);
        background: black 10%;
        text-wrap: nowrap;
        text-overflow: clip;        
        &:light {
            background: white 30%;
        }
    }

    MarkdownFence > * {
        width: auto;
    }
    """

    def __init__(self, markdown: Markdown, code: str, lexer: str) -> None:
        super().__init__(markdown)
        self.code = code
        self.lexer = lexer
        self.theme = (
            self._markdown.code_dark_theme
            if self.app.current_theme.dark
            else self._markdown.code_light_theme
        )
        code_content = highlight(self.code, language=lexer)
        self.set_content(code_content)


HEADINGS = {
    "h1": MarkdownH1,
    "h2": MarkdownH2,
    "h3": MarkdownH3,
    "h4": MarkdownH4,
    "h5": MarkdownH5,
    "h6": MarkdownH6,
}

NUMERALS = " ⅠⅡⅢⅣⅤⅥ"


class Markdown(Widget):
    DEFAULT_CSS = """
    Markdown {        
        height: auto;
        padding: 0 2 1 2;
        layout: vertical;
        color: $foreground;
        # background: $surface;
        overflow-y: hidden;
        
        &:focus {
            background-tint: $foreground 5%;
        }
        &:dark .code_inline {
            background: $warning-muted 30%;
            color: $warning;        
        }
        &:light .code_inline {
            background: $error-muted 30%;
            color: $error;
        }
    }
    .em {
        text-style: italic;        
    }
    .strong {
        text-style: bold;
    }
    .s {
        text-style: strike;
    }
    
    """

    COMPONENT_CLASSES = {"em", "strong", "s", "code_inline"}
    """
    These component classes target standard inline markdown styles.
    Changing these will potentially break the standard markdown formatting.

    | Class | Description |
    | :- | :- |
    | `code_inline` | Target text that is styled as inline code. |
    | `em` | Target text that is emphasized inline. |
    | `s` | Target text that is styled inline with strikethrough. |
    | `strong` | Target text that is styled inline with strong. |
    """

    BULLETS = ["\u25cf ", "▪ ", "‣ ", "• ", "⭑ "]

    code_dark_theme: reactive[str] = reactive("material")
    """The theme to use for code blocks when the App theme is dark."""

    code_light_theme: reactive[str] = reactive("material-light")
    """The theme to use for code blocks when the App theme is light."""

    code_indent_guides: reactive[bool] = reactive(True)
    """Should code fences display indent guides?"""

    def __init__(
        self,
        markdown: str | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        parser_factory: Callable[[], MarkdownIt] | None = None,
        open_links: bool = True,
    ):
        """A Markdown widget.

        Args:
            markdown: String containing Markdown or None to leave blank for now.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes of the widget.
            parser_factory: A factory function to return a configured MarkdownIt instance. If `None`, a "gfm-like" parser is used.
            open_links: Open links automatically. If you set this to `False`, you can handle the [`LinkClicked`][textual.widgets.markdown.Markdown.LinkClicked] events.
        """
        super().__init__(name=name, id=id, classes=classes)
        self._initial_markdown: str | None = markdown
        self._markdown = ""
        self._parser_factory = parser_factory
        self._table_of_contents: TableOfContentsType = []
        self._open_links = open_links
        self._last_parsed_line = 0

    class TableOfContentsUpdated(Message):
        """The table of contents was updated."""

        def __init__(
            self, markdown: Markdown, table_of_contents: TableOfContentsType
        ) -> None:
            super().__init__()
            self.markdown: Markdown = markdown
            """The `Markdown` widget associated with the table of contents."""
            self.table_of_contents: TableOfContentsType = table_of_contents
            """Table of contents."""

        @property
        def control(self) -> Markdown:
            """The `Markdown` widget associated with the table of contents.

            This is an alias for [`TableOfContentsUpdated.markdown`][textual.widgets.Markdown.TableOfContentsSelected.markdown]
            and is used by the [`on`][textual.on] decorator.
            """
            return self.markdown

    class TableOfContentsSelected(Message):
        """An item in the TOC was selected."""

        def __init__(self, markdown: Markdown, block_id: str) -> None:
            super().__init__()
            self.markdown: Markdown = markdown
            """The `Markdown` widget where the selected item is."""
            self.block_id: str = block_id
            """ID of the block that was selected."""

        @property
        def control(self) -> Markdown:
            """The `Markdown` widget where the selected item is.

            This is an alias for [`TableOfContentsSelected.markdown`][textual.widgets.Markdown.TableOfContentsSelected.markdown]
            and is used by the [`on`][textual.on] decorator.
            """
            return self.markdown

    class LinkClicked(Message):
        """A link in the document was clicked."""

        def __init__(self, markdown: Markdown, href: str) -> None:
            super().__init__()
            self.markdown: Markdown = markdown
            """The `Markdown` widget containing the link clicked."""
            self.href: str = unquote(href)
            """The link that was selected."""

        @property
        def control(self) -> Markdown:
            """The `Markdown` widget containing the link clicked.

            This is an alias for [`LinkClicked.markdown`][textual.widgets.Markdown.LinkClicked.markdown]
            and is used by the [`on`][textual.on] decorator.
            """
            return self.markdown

    @property
    def source(self) -> str:
        """The markdown source."""
        return self._markdown or ""

    def notify_style_update(self) -> None:
        self.update(self.source)
        super().notify_style_update()

    async def _on_mount(self, _: Mount) -> None:
        initial_markdown = self._initial_markdown
        self._initial_markdown = None
        await self.update(initial_markdown or "")

        if initial_markdown is None:
            self.post_message(
                Markdown.TableOfContentsUpdated(
                    self, self._table_of_contents
                ).set_sender(self)
            )

    @classmethod
    def get_stream(cls, markdown: Markdown) -> MarkdownStream:
        """Get a [MarkdownStream][textual.widgets._markdown.MarkdownStream] instance stream Markdown in the background.

        If you append to the Markdown document many times a second, it is possible the widget won't
        be able to update as fast as you write (occurs around 20 appends per second). It will still
        work, but the user will have to wait for the UI to catch up after the document has be retrieved.

        Using a [MarkdownStream][textual.widgets._markdown.MarkdownStream] will combine several updates in to one
        as necessary to keep up with the incoming data.

        example:
        ```python
        # self.get_chunk is a hypothetical method that retrieves a
        # markdown fragment from the network
        @work
        async def stream_markdown(self) -> None:
            markdown_widget = self.query_one(Markdown)
            container = self.query_one(VerticalScroll)
            container.anchor()

            stream = Markdown.get_stream(markdown_widget)
            try:
                while (chunk:= await self.get_chunk()) is not None:
                    await stream.write(chunk)
            finally:
                await stream.stop()
        ```


        Args:
            markdown: A [Markdown][textual.widgets.Markdown] widget instance.

        Returns:
            The Markdown stream object.
        """
        updater = MarkdownStream(markdown)
        updater.start()
        return updater

    def on_markdown_link_clicked(self, event: LinkClicked) -> None:
        if self._open_links:
            self.app.open_url(event.href)

    def _watch_code_dark_theme(self) -> None:
        """React to the dark theme being changed."""
        if self.app.current_theme.dark:
            for block in self.query(MarkdownFence):
                block._retheme()

    def _watch_code_light_theme(self) -> None:
        """React to the light theme being changed."""
        if not self.app.current_theme.dark:
            for block in self.query(MarkdownFence):
                block._retheme()

    @staticmethod
    def sanitize_location(location: str) -> tuple[Path, str]:
        """Given a location, break out the path and any anchor.

        Args:
            location: The location to sanitize.

        Returns:
            A tuple of the path to the location cleaned of any anchor, plus
            the anchor (or an empty string if none was found).
        """
        location, _, anchor = location.partition("#")
        return Path(location), anchor

    def goto_anchor(self, anchor: str) -> bool:
        """Try and find the given anchor in the current document.

        Args:
            anchor: The anchor to try and find.

        Note:
            The anchor is found by looking at all of the headings in the
            document and finding the first one whose slug matches the
            anchor.

            Note that the slugging method used is similar to that found on
            GitHub.

        Returns:
            True when the anchor was found in the current document, False otherwise.
        """
        if not self._table_of_contents or not isinstance(self.parent, Widget):
            return False
        unique = TrackedSlugs()
        for _, title, header_id in self._table_of_contents:
            if unique.slug(title) == anchor:
                self.query_one(f"#{header_id}").scroll_visible(top=True)
                return True
        return False

    async def load(self, path: Path) -> None:
        """Load a new Markdown document.

        Args:
            path: Path to the document.

        Raises:
            OSError: If there was some form of error loading the document.

        Note:
            The exceptions that can be raised by this method are all of
            those that can be raised by calling [`Path.read_text`][pathlib.Path.read_text].
        """
        path, anchor = self.sanitize_location(str(path))
        data = await asyncio.get_running_loop().run_in_executor(
            None, partial(path.read_text, encoding="utf-8")
        )
        await self.update(data)
        if anchor:
            self.goto_anchor(anchor)

    def unhandled_token(self, token: Token) -> MarkdownBlock | None:
        """Process an unhandled token.

        Args:
            token: The MarkdownIt token to handle.

        Returns:
            Either a widget to be added to the output, or `None`.
        """
        return None

    def _parse_markdown(
        self,
        tokens: Iterable[Token],
        table_of_contents: TableOfContentsType,
    ) -> Iterable[MarkdownBlock]:
        """Create a stream of MarkdownBlock widgets from markdown.

        Args:
            tokens: List of tokens.
            table_of_contents: List to store table of contents.

        Yields:
            Widgets for mounting.
        """

        stack: list[MarkdownBlock] = []
        stack_append = stack.append

        for token in tokens:
            token_type = token.type
            if token_type == "heading_open":
                stack_append(HEADINGS[token.tag](self))
            elif token_type == "hr":
                yield MarkdownHorizontalRule(self)
            elif token_type == "paragraph_open":
                stack_append(MarkdownParagraph(self))
            elif token_type == "blockquote_open":
                stack_append(MarkdownBlockQuote(self))
            elif token_type == "bullet_list_open":
                stack_append(MarkdownBulletList(self))
            elif token_type == "ordered_list_open":
                stack_append(MarkdownOrderedList(self))
            elif token_type == "list_item_open":
                if token.info:
                    stack_append(MarkdownOrderedListItem(self, token.info))
                else:
                    item_count = sum(
                        1
                        for block in stack
                        if isinstance(block, MarkdownUnorderedListItem)
                    )
                    stack_append(
                        MarkdownUnorderedListItem(
                            self,
                            self.BULLETS[item_count % len(self.BULLETS)],
                        )
                    )
            elif token_type == "table_open":
                stack_append(MarkdownTable(self))
            elif token_type == "tbody_open":
                stack_append(MarkdownTBody(self))
            elif token_type == "thead_open":
                stack_append(MarkdownTHead(self))
            elif token_type == "tr_open":
                stack_append(MarkdownTR(self))
            elif token_type == "th_open":
                stack_append(MarkdownTH(self))
            elif token_type == "td_open":
                stack_append(MarkdownTD(self))
            elif token_type.endswith("_close"):
                block = stack.pop()
                if token.type == "heading_close":
                    heading = block._content.plain
                    level = int(token.tag[1:])
                    block.id = f"{slug(heading)}-{len(table_of_contents) + 1}"
                    table_of_contents.append((level, heading, block.id))
                if stack:
                    stack[-1]._blocks.append(block)
                else:
                    yield block
            elif token_type == "inline":
                stack[-1].build_from_token(token)
            elif token_type in ("fence", "code_block"):
                fence = MarkdownFence(self, token.content.rstrip(), token.info)
                if stack:
                    stack[-1]._blocks.append(fence)
                else:
                    yield fence
            else:
                external = self.unhandled_token(token)
                if external is not None:
                    if stack:
                        stack[-1]._blocks.append(external)
                    else:
                        yield external

    def update(self, markdown: str) -> AwaitComplete:
        """Update the document with new Markdown.

        Args:
            markdown: A string containing Markdown.

        Returns:
            An optionally awaitable object. Await this to ensure that all children have been mounted.
        """
        parser = (
            MarkdownIt("gfm-like")
            if self._parser_factory is None
            else self._parser_factory()
        )

        table_of_contents: TableOfContentsType = []
        markdown_block = self.query("MarkdownBlock")
        self._markdown = markdown

        async def await_update() -> None:
            """Update in batches."""
            BATCH_SIZE = 200
            batch: list[MarkdownBlock] = []

            # Lock so that you can't update with more than one document simultaneously
            async with self.lock:
                tokens = await asyncio.get_running_loop().run_in_executor(
                    None, parser.parse, markdown
                )

                # Remove existing blocks for the first batch only
                removed: bool = False

                async def mount_batch(batch: list[MarkdownBlock]) -> None:
                    """Mount a single match of blocks.

                    Args:
                        batch: A list of blocks to mount.
                    """
                    nonlocal removed
                    if removed:
                        await self.mount_all(batch)
                    else:
                        with self.app.batch_update():
                            await markdown_block.remove()
                            await self.mount_all(batch)
                        removed = True

                for block in self._parse_markdown(tokens, table_of_contents):
                    batch.append(block)
                    if len(batch) == BATCH_SIZE:
                        await mount_batch(batch)
                        batch.clear()
                if batch:
                    await mount_batch(batch)
                if not removed:
                    await markdown_block.remove()

            if table_of_contents != self._table_of_contents:
                self._table_of_contents = table_of_contents
                self.post_message(
                    Markdown.TableOfContentsUpdated(
                        self, self._table_of_contents
                    ).set_sender(self)
                )

        return AwaitComplete(await_update())

    def append(self, markdown: str) -> AwaitComplete:
        """Append to markdown.

        Args:
            markdown: A fragment of markdown to be appended.

        Returns:
            An optionally awaitable object. Await this to ensure that the markdown has been append by the next line.
        """
        parser = (
            MarkdownIt("gfm-like")
            if self._parser_factory is None
            else self._parser_factory()
        )

        table_of_contents: TableOfContentsType = []
        self._markdown = self.source + markdown
        updated_source = "\n".join(
            self._markdown.splitlines()[self._last_parsed_line :]
        )

        async def await_append() -> None:
            """Append new markdown widgets."""
            async with self.lock:
                tokens = parser.parse(updated_source)
                existing_blocks = [
                    child for child in self.children if isinstance(child, MarkdownBlock)
                ]
                for token in reversed(tokens):
                    if token.map is not None and token.level == 0:
                        self._last_parsed_line += token.map[0]
                        break
                new_blocks = list(self._parse_markdown(tokens, table_of_contents))
                with self.app.batch_update():
                    if existing_blocks and new_blocks:
                        last_block = existing_blocks[-1]
                        try:
                            await last_block._update_from_block(new_blocks[0])
                        except IndexError:
                            pass
                        else:
                            new_blocks = new_blocks[1:]

                    if new_blocks:
                        await self.mount_all(new_blocks)

                self._table_of_contents = table_of_contents
                self.post_message(
                    Markdown.TableOfContentsUpdated(
                        self, self._table_of_contents
                    ).set_sender(self)
                )

        return AwaitComplete(await_append())


class MarkdownTableOfContents(Widget, can_focus_children=True):
    """Displays a table of contents for a markdown document."""

    DEFAULT_CSS = """
    MarkdownTableOfContents {
        width: auto;
        height: 1fr;
        background: $panel;
        &:focus-within {
            background-tint: $foreground 5%;
        }
    }
    MarkdownTableOfContents > Tree {
        padding: 1;
        width: auto;
        height: 1fr;
        background: $panel;
    }
    """

    table_of_contents = reactive[Optional[TableOfContentsType]](None, init=False)
    """Underlying data to populate the table of contents widget."""

    def __init__(
        self,
        markdown: Markdown,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialize a table of contents.

        Args:
            markdown: The Markdown document associated with this table of contents.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
        """
        self.markdown: Markdown = markdown
        """The Markdown document associated with this table of contents."""
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

    def compose(self) -> ComposeResult:
        tree: Tree = Tree("TOC")
        tree.show_root = False
        tree.show_guides = True
        tree.guide_depth = 4
        tree.auto_expand = False
        yield tree

    def watch_table_of_contents(self, table_of_contents: TableOfContentsType) -> None:
        """Triggered when the table of contents changes."""
        self.rebuild_table_of_contents(table_of_contents)

    def rebuild_table_of_contents(self, table_of_contents: TableOfContentsType) -> None:
        """Rebuilds the tree representation of the table of contents data.

        Args:
            table_of_contents: Table of contents.
        """
        tree = self.query_one(Tree)
        tree.clear()
        root = tree.root
        for level, name, block_id in table_of_contents:
            node = root
            for _ in range(level - 1):
                if node._children:
                    node = node._children[-1]
                    node.expand()
                    node.allow_expand = True
                else:
                    node = node.add(NUMERALS[level], expand=True)
            node_label = Text.assemble((f"{NUMERALS[level]} ", "dim"), name)
            node.add_leaf(node_label, {"block_id": block_id})

    async def _on_tree_node_selected(self, message: Tree.NodeSelected) -> None:
        node_data = message.node.data
        if node_data is not None:
            await self._post_message(
                Markdown.TableOfContentsSelected(self.markdown, node_data["block_id"])
            )
        message.stop()


class MarkdownViewer(VerticalScroll, can_focus=False, can_focus_children=True):
    """A Markdown viewer widget."""

    SCOPED_CSS = False

    DEFAULT_CSS = """
    MarkdownViewer {
        height: 1fr;
        scrollbar-gutter: stable;
        background: $surface;
        & > MarkdownTableOfContents {
            display: none;
            dock:left;
        }
    }

    MarkdownViewer.-show-table-of-contents > MarkdownTableOfContents {
        display: block;
    }
    """

    show_table_of_contents = reactive(True)
    """Show the table of contents?"""
    code_indent_guides: reactive[bool] = reactive(True)
    """Should code fences display indent guides?"""
    top_block = reactive("")

    navigator: var[Navigator] = var(Navigator)

    class NavigatorUpdated(Message):
        """Navigator has been changed (clicked link etc)."""

    def __init__(
        self,
        markdown: str | None = None,
        *,
        show_table_of_contents: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        parser_factory: Callable[[], MarkdownIt] | None = None,
        open_links: bool = True,
    ):
        """Create a Markdown Viewer object.

        Args:
            markdown: String containing Markdown, or None to leave blank.
            show_table_of_contents: Show a table of contents in a sidebar.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes of the widget.
            parser_factory: A factory function to return a configured MarkdownIt instance. If `None`, a "gfm-like" parser is used.
            open_links: Open links automatically. If you set this to `False`, you can handle the [`LinkClicked`][textual.widgets.markdown.Markdown.LinkClicked] events.
        """
        super().__init__(name=name, id=id, classes=classes)
        self.show_table_of_contents = show_table_of_contents
        self._markdown = markdown
        self._parser_factory = parser_factory
        self._open_links = open_links

    @property
    def document(self) -> Markdown:
        """The [`Markdown`][textual.widgets.Markdown] document widget."""
        return self.query_one(Markdown)

    @property
    def table_of_contents(self) -> MarkdownTableOfContents:
        """The [table of contents][textual.widgets.markdown.MarkdownTableOfContents] widget."""
        return self.query_one(MarkdownTableOfContents)

    async def _on_mount(self, _: Mount) -> None:
        await self.document.update(self._markdown or "")

    async def go(self, location: str | PurePath) -> None:
        """Navigate to a new document path."""
        path, anchor = self.document.sanitize_location(str(location))
        if path == Path(".") and anchor:
            # We've been asked to go to an anchor but with no file specified.
            self.document.goto_anchor(anchor)
        else:
            # We've been asked to go to a file, optionally with an anchor.
            await self.document.load(self.navigator.go(location))
            self.post_message(self.NavigatorUpdated())

    async def back(self) -> None:
        """Go back one level in the history."""
        if self.navigator.back():
            await self.document.load(self.navigator.location)
            self.post_message(self.NavigatorUpdated())

    async def forward(self) -> None:
        """Go forward one level in the history."""
        if self.navigator.forward():
            await self.document.load(self.navigator.location)
            self.post_message(self.NavigatorUpdated())

    async def _on_markdown_link_clicked(self, message: Markdown.LinkClicked) -> None:
        message.stop()
        await self.go(message.href)

    def watch_show_table_of_contents(self, show_table_of_contents: bool) -> None:
        self.set_class(show_table_of_contents, "-show-table-of-contents")

    def compose(self) -> ComposeResult:
        markdown = Markdown(
            parser_factory=self._parser_factory, open_links=self._open_links
        )
        markdown.can_focus = True
        yield markdown.data_bind(MarkdownViewer.code_indent_guides)
        yield MarkdownTableOfContents(markdown)

    def _on_markdown_table_of_contents_updated(
        self, message: Markdown.TableOfContentsUpdated
    ) -> None:
        self.query_one(MarkdownTableOfContents).table_of_contents = (
            message.table_of_contents
        )
        message.stop()

    def _on_markdown_table_of_contents_selected(
        self, message: Markdown.TableOfContentsSelected
    ) -> None:
        block_selector = f"#{message.block_id}"
        block = self.query_one(block_selector, MarkdownBlock)
        self.scroll_to_widget(block, top=True)
        message.stop()
