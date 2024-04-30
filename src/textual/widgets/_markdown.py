from __future__ import annotations

import re
from pathlib import Path, PurePath
from typing import Callable, Iterable, Optional

from markdown_it import MarkdownIt
from markdown_it.token import Token
from rich import box
from rich.style import Style
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from typing_extensions import TypeAlias

from .._slug import TrackedSlugs
from ..app import ComposeResult
from ..await_complete import AwaitComplete
from ..containers import Horizontal, Vertical, VerticalScroll
from ..events import Mount
from ..message import Message
from ..reactive import reactive, var
from ..widget import Widget
from ..widgets import Static, Tree

TableOfContentsType: TypeAlias = "list[tuple[int, str, str | None]]"
"""Information about the table of contents of a markdown document.

The triples encode the level, the label, and the optional block id of each heading.
"""


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
        height: auto;
    }
    """

    def __init__(self, markdown: Markdown, *args, **kwargs) -> None:
        self._markdown: Markdown = markdown
        """A reference to the Markdown document that contains this block."""
        self._text = Text()
        self._token: Token | None = None
        self._blocks: list[MarkdownBlock] = []
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield from self._blocks
        self._blocks.clear()

    def set_content(self, text: Text) -> None:
        self._text = text
        self.update(text)

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
        style_stack: list[Style] = [Style()]
        content = Text()
        if token.children:
            for child in token.children:
                if child.type == "text":
                    content.append(
                        # Ensure repeating spaces and/or tabs get squashed
                        # down to a single space.
                        re.sub(r"\s+", " ", child.content),
                        style_stack[-1],
                    )
                if child.type == "hardbreak":
                    content.append("\n")
                if child.type == "softbreak":
                    content.append(" ", style_stack[-1])
                elif child.type == "code_inline":
                    content.append(
                        child.content,
                        style_stack[-1]
                        + self._markdown.get_component_rich_style(
                            "code_inline", partial=True
                        ),
                    )
                elif child.type == "em_open":
                    style_stack.append(
                        style_stack[-1]
                        + self._markdown.get_component_rich_style("em", partial=True)
                    )
                elif child.type == "strong_open":
                    style_stack.append(
                        style_stack[-1]
                        + self._markdown.get_component_rich_style(
                            "strong", partial=True
                        )
                    )
                elif child.type == "s_open":
                    style_stack.append(
                        style_stack[-1]
                        + self._markdown.get_component_rich_style("s", partial=True)
                    )
                elif child.type == "link_open":
                    href = child.attrs.get("href", "")
                    action = f"link({href!r})"
                    style_stack.append(
                        style_stack[-1] + Style.from_meta({"@click": action})
                    )
                elif child.type == "image":
                    href = child.attrs.get("src", "")
                    alt = child.attrs.get("alt", "")

                    action = f"link({href!r})"
                    style_stack.append(
                        style_stack[-1] + Style.from_meta({"@click": action})
                    )

                    content.append("🖼  ", style_stack[-1])
                    if alt:
                        content.append(f"({alt})", style_stack[-1])
                    if child.children is not None:
                        for grandchild in child.children:
                            content.append(grandchild.content, style_stack[-1])

                    style_stack.pop()

                elif child.type.endswith("_close"):
                    style_stack.pop()

        self.set_content(content)


class MarkdownHeader(MarkdownBlock):
    """Base class for a Markdown header."""

    DEFAULT_CSS = """
    MarkdownHeader {
        color: $text;
    }
    """


class MarkdownH1(MarkdownHeader):
    """An H1 Markdown header."""

    DEFAULT_CSS = """

    MarkdownH1 {
        background: $accent-darken-2;
        border: wide $background;
        content-align: center middle;

        padding: 1;
        text-style: bold;
        color: $text;
    }
    """


class MarkdownH2(MarkdownHeader):
    """An H2 Markdown header."""

    DEFAULT_CSS = """

    MarkdownH2 {
        background: $panel;
        border: wide $background;
        text-align: center;
        text-style: underline;
        color: $text;
        padding: 1;
        text-style: bold;
    }
    """


class MarkdownH3(MarkdownHeader):
    """An H3 Markdown header."""

    DEFAULT_CSS = """
    MarkdownH3 {
        background: $surface;
        text-style: bold;
        color: $text;
        border-bottom: wide $foreground;
        width: auto;
    }
    """


class MarkdownH4(MarkdownHeader):
    """An H4 Markdown header."""

    DEFAULT_CSS = """
    MarkdownH4 {
        text-style: underline;
        margin: 1 0;
    }
    """


class MarkdownH5(MarkdownHeader):
    """An H5 Markdown header."""

    DEFAULT_CSS = """
    MarkdownH5 {
        text-style: bold;
        color: $text;
        margin: 1 0;
    }
    """


class MarkdownH6(MarkdownHeader):
    """An H6 Markdown header."""

    DEFAULT_CSS = """
    MarkdownH6 {
        text-style: bold;
        color: $text-muted;
        margin: 1 0;
    }
    """


class MarkdownHorizontalRule(MarkdownBlock):
    """A horizontal rule."""

    DEFAULT_CSS = """
    MarkdownHorizontalRule {
        border-bottom: heavy $primary;
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
        border-left: outer $success;
        margin: 1 0;
        padding: 0 1;
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


class MarkdownTableContent(Widget):
    """Renders a Markdown table."""

    DEFAULT_CSS = """
    MarkdownTableContent {
        width: 100%;
        height: auto;

    }
    MarkdownTableContent > .markdown-table--header {
        text-style: bold;
    }
    """

    COMPONENT_CLASSES = {"markdown-table--header", "markdown-table--lines"}

    def __init__(self, headers: list[Text], rows: list[list[Text]]):
        self.headers = headers
        """List of header text."""
        self.rows = rows
        """The row contents."""
        super().__init__()
        self.shrink = True

    def render(self) -> Table:
        table = Table(
            expand=True,
            box=box.SIMPLE_HEAVY,
            style=self.rich_style,
            header_style=self.get_component_rich_style("markdown-table--header"),
            border_style=self.get_component_rich_style("markdown-table--lines"),
            collapse_padding=True,
            padding=0,
        )
        for header in self.headers:
            table.add_column(header)
        for row in self.rows:
            if row:
                table.add_row(*row)
        return table


class MarkdownTable(MarkdownBlock):
    """A Table markdown Block."""

    DEFAULT_CSS = """
    MarkdownTable {
        width: 100%;
        margin: 1 0;
        background: $panel;
        border: wide $background;
    }
    """

    def compose(self) -> ComposeResult:
        def flatten(block: MarkdownBlock) -> Iterable[MarkdownBlock]:
            for block in block._blocks:
                if block._blocks:
                    yield from flatten(block)
                yield block

        headers: list[Text] = []
        rows: list[list[Text]] = []
        for block in flatten(self):
            if isinstance(block, MarkdownTH):
                headers.append(block._text)
            elif isinstance(block, MarkdownTR):
                rows.append([])
            elif isinstance(block, MarkdownTD):
                rows[-1].append(block._text)

        yield MarkdownTableContent(headers, rows)
        self._blocks.clear()


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
        color: $success;
        text-style: bold;
    }
    """

    symbol = reactive("\u25cf")
    """The symbol for the bullet."""

    def render(self) -> Text:
        return Text(self.symbol)


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
        margin: 1 0;
        overflow: auto;
        width: 100%;
        height: auto;
        max-height: 20;
        color: rgb(210,210,210);
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
            if self.app.dark
            else self._markdown.code_light_theme
        )

    def _block(self) -> Syntax:
        return Syntax(
            self.code,
            lexer=self.lexer,
            word_wrap=False,
            indent_guides=True,
            padding=(1, 2),
            theme=self.theme,
        )

    def _on_mount(self, _: Mount) -> None:
        """Watch app theme switching."""
        self.watch(self.app, "dark", self._retheme)

    def _retheme(self) -> None:
        """Rerender when the theme changes."""
        self.theme = (
            self._markdown.code_dark_theme
            if self.app.dark
            else self._markdown.code_light_theme
        )
        self.get_child_by_type(Static).update(self._block())

    def compose(self) -> ComposeResult:
        yield Static(
            self._block(),
            expand=True,
            shrink=False,
        )


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
        margin: 0 4 1 4;
        layout: vertical;
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
    .code_inline {
        text-style: bold dim;
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
    | `s` | Target text that is styled inline with strykethrough. |
    | `strong` | Target text that is styled inline with strong. |
    """

    BULLETS = ["\u25cf ", "▪ ", "‣ ", "• ", "⭑ "]

    code_dark_theme: reactive[str] = reactive("material")
    """The theme to use for code blocks when in [dark mode][textual.app.App.dark]."""

    code_light_theme: reactive[str] = reactive("material-light")
    """The theme to use for code blocks when in [light mode][textual.app.App.dark]."""

    def __init__(
        self,
        markdown: str | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        parser_factory: Callable[[], MarkdownIt] | None = None,
    ):
        """A Markdown widget.

        Args:
            markdown: String containing Markdown or None to leave blank for now.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes of the widget.
            parser_factory: A factory function to return a configured MarkdownIt instance. If `None`, a "gfm-like" parser is used.
        """
        super().__init__(name=name, id=id, classes=classes)
        self._markdown = markdown
        self._parser_factory = parser_factory
        self._table_of_contents: TableOfContentsType | None = None

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
            self.href: str = href
            """The link that was selected."""

        @property
        def control(self) -> Markdown:
            """The `Markdown` widget containing the link clicked.

            This is an alias for [`LinkClicked.markdown`][textual.widgets.Markdown.LinkClicked.markdown]
            and is used by the [`on`][textual.on] decorator.
            """
            return self.markdown

    async def _on_mount(self, _: Mount) -> None:
        if self._markdown is not None:
            await self.update(self._markdown)

    def _watch_code_dark_theme(self) -> None:
        """React to the dark theme being changed."""
        if self.app.dark:
            for block in self.query(MarkdownFence):
                block._retheme()

    def _watch_code_light_theme(self) -> None:
        """React to the light theme being changed."""
        if not self.app.dark:
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
                self.parent.scroll_to_widget(self.query_one(f"#{header_id}"), top=True)
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
        await self.update(path.read_text(encoding="utf-8"))
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

    def update(self, markdown: str) -> AwaitComplete:
        """Update the document with new Markdown.

        Args:
            markdown: A string containing Markdown.

        Returns:
            An optionally awaitable object. Await this to ensure that all children have been mounted.
        """
        output: list[MarkdownBlock] = []
        stack: list[MarkdownBlock] = []
        parser = (
            MarkdownIt("gfm-like")
            if self._parser_factory is None
            else self._parser_factory()
        )

        block_id: int = 0
        self._table_of_contents = []

        for token in parser.parse(markdown):
            if token.type == "heading_open":
                block_id += 1
                stack.append(HEADINGS[token.tag](self, id=f"block{block_id}"))
            elif token.type == "hr":
                output.append(MarkdownHorizontalRule(self))
            elif token.type == "paragraph_open":
                stack.append(MarkdownParagraph(self))
            elif token.type == "blockquote_open":
                stack.append(MarkdownBlockQuote(self))
            elif token.type == "bullet_list_open":
                stack.append(MarkdownBulletList(self))
            elif token.type == "ordered_list_open":
                stack.append(MarkdownOrderedList(self))
            elif token.type == "list_item_open":
                if token.info:
                    stack.append(MarkdownOrderedListItem(self, token.info))
                else:
                    item_count = sum(
                        1
                        for block in stack
                        if isinstance(block, MarkdownUnorderedListItem)
                    )
                    stack.append(
                        MarkdownUnorderedListItem(
                            self,
                            self.BULLETS[item_count % len(self.BULLETS)],
                        )
                    )

            elif token.type == "table_open":
                stack.append(MarkdownTable(self))
            elif token.type == "tbody_open":
                stack.append(MarkdownTBody(self))
            elif token.type == "thead_open":
                stack.append(MarkdownTHead(self))
            elif token.type == "tr_open":
                stack.append(MarkdownTR(self))
            elif token.type == "th_open":
                stack.append(MarkdownTH(self))
            elif token.type == "td_open":
                stack.append(MarkdownTD(self))
            elif token.type.endswith("_close"):
                block = stack.pop()
                if token.type == "heading_close":
                    heading = block._text.plain
                    level = int(token.tag[1:])
                    self._table_of_contents.append((level, heading, block.id))
                if stack:
                    stack[-1]._blocks.append(block)
                else:
                    output.append(block)
            elif token.type == "inline":
                stack[-1].build_from_token(token)
            elif token.type in ("fence", "code_block"):
                (stack[-1]._blocks if stack else output).append(
                    MarkdownFence(self, token.content.rstrip(), token.info)
                )
            else:
                external = self.unhandled_token(token)
                if external is not None:
                    (stack[-1]._blocks if stack else output).append(external)

        self.post_message(
            Markdown.TableOfContentsUpdated(self, self._table_of_contents).set_sender(
                self
            )
        )
        markdown_block = self.query("MarkdownBlock")

        async def await_update() -> None:
            """Update in a single batch."""

            with self.app.batch_update():
                await markdown_block.remove()
                await self.mount_all(output)

        return AwaitComplete(await_update())


class MarkdownTableOfContents(Widget, can_focus_children=True):
    """Displays a table of contents for a markdown document."""

    DEFAULT_CSS = """
    MarkdownTableOfContents {
        width: auto;
        background: $panel;
        border-right: wide $background;
    }
    MarkdownTableOfContents > Tree {
        padding: 1;
        width: auto;
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


class MarkdownViewer(VerticalScroll, can_focus=True, can_focus_children=True):
    """A Markdown viewer widget."""

    SCOPED_CSS = False

    DEFAULT_CSS = """
    MarkdownViewer {
        height: 1fr;
        scrollbar-gutter: stable;
    }

    MarkdownTableOfContents {
        dock:left;
    }

    MarkdownViewer > MarkdownTableOfContents {
        display: none;
    }

    MarkdownViewer.-show-table-of-contents > MarkdownTableOfContents {
        display: block;
    }
    """

    show_table_of_contents = reactive(True)
    top_block = reactive("")

    navigator: var[Navigator] = var(Navigator)

    def __init__(
        self,
        markdown: str | None = None,
        *,
        show_table_of_contents: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        parser_factory: Callable[[], MarkdownIt] | None = None,
    ):
        """Create a Markdown Viewer object.

        Args:
            markdown: String containing Markdown, or None to leave blank.
            show_table_of_contents: Show a table of contents in a sidebar.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes of the widget.
            parser_factory: A factory function to return a configured MarkdownIt instance. If `None`, a "gfm-like" parser is used.
        """
        super().__init__(name=name, id=id, classes=classes)
        self.show_table_of_contents = show_table_of_contents
        self._markdown = markdown
        self._parser_factory = parser_factory

    @property
    def document(self) -> Markdown:
        """The [`Markdown`][textual.widgets.Markdown] document widget."""
        return self.query_one(Markdown)

    @property
    def table_of_contents(self) -> MarkdownTableOfContents:
        """The [table of contents][textual.widgets.markdown.MarkdownTableOfContents] widget."""
        return self.query_one(MarkdownTableOfContents)

    def _on_mount(self, _: Mount) -> None:
        if self._markdown is not None:
            self.document.update(self._markdown)

    async def go(self, location: str | PurePath) -> None:
        """Navigate to a new document path."""
        path, anchor = self.document.sanitize_location(str(location))
        if path == Path(".") and anchor:
            # We've been asked to go to an anchor but with no file specified.
            self.document.goto_anchor(anchor)
        else:
            # We've been asked to go to a file, optionally with an anchor.
            await self.document.load(self.navigator.go(location))

    async def back(self) -> None:
        """Go back one level in the history."""
        if self.navigator.back():
            await self.document.load(self.navigator.location)

    async def forward(self) -> None:
        """Go forward one level in the history."""
        if self.navigator.forward():
            await self.document.load(self.navigator.location)

    async def _on_markdown_link_clicked(self, message: Markdown.LinkClicked) -> None:
        message.stop()
        await self.go(message.href)

    def watch_show_table_of_contents(self, show_table_of_contents: bool) -> None:
        self.set_class(show_table_of_contents, "-show-table-of-contents")

    def compose(self) -> ComposeResult:
        markdown = Markdown(parser_factory=self._parser_factory)
        yield MarkdownTableOfContents(markdown)
        yield markdown

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
