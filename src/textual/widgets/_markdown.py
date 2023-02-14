from __future__ import annotations

from pathlib import Path
from typing import Iterable

from markdown_it import MarkdownIt
from rich.style import Style
from rich.syntax import Syntax
from rich.text import Text
from typing_extensions import TypeAlias

from ..app import ComposeResult
from ..containers import Vertical
from ..message import Message
from ..reactive import reactive, var
from ..widget import Widget
from ..widgets import DataTable, Static, Tree

TOC: TypeAlias = "list[tuple[int, str, str | None]]"


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

    def go(self, path: str) -> Path:
        """Go to a new document.

        Args:
            path: Path to new document.

        Returns:
            Path: New location.
        """
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


class Block(Static):
    """The base class for a Markdown Element."""

    DEFAULT_CSS = """
    Block {
        height: auto;
    }
    """

    def __init__(self, *args, **kwargs) -> None:
        self.text = Text()
        self.blocks: list[Block] = []
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield from self.blocks
        self.blocks.clear()

    def set_content(self, text: Text) -> None:
        self.text = text
        self.update(text)

    async def action_link(self, href: str) -> None:
        """Called on link click."""
        await self.post_message(Markdown.LinkClicked(href, sender=self))


class Header(Block):
    """Base class for a Markdown header."""

    DEFAULT_CSS = """
    Header {
        color: $text;
    }
    """


class H1(Header):
    """An H1 Markdown header."""

    DEFAULT_CSS = """

    H1 {
        background: $accent-darken-2;
        border: wide $background;
        content-align: center middle;

        padding: 1;
        text-style: bold;
        color: $text;
    }

    """


class H2(Header):
    """An H2 Markdown header."""

    DEFAULT_CSS = """

    H2 {
        background: $panel;
        border: wide $background;
        text-align: center;
        text-style: underline;
        color: $text;
        padding: 1;
        text-style: bold;
    }

    """


class H3(Header):
    """An H3 Markdown header."""

    DEFAULT_CSS = """
    H3 {
        background: $surface;
        text-style: bold;
        color: $text;
        border-bottom: wide $foreground;
        width: auto;
    }
    """


class H4(Header):
    """An H4 Markdown header."""

    DEFAULT_CSS = """
    H4 {
        text-style: underline;
        margin: 1 0;
    }

    """


class H5(Header):
    """An H5 Markdown header."""

    DEFAULT_CSS = """
    H5 {
        text-style: bold;
        color: $text;
        margin: 1 0;
    }

    """


class H6(Header):
    """An H6 Markdown header."""

    DEFAULT_CSS = """
    H6 {
        text-style: bold;
        color: $text-muted;
        margin: 1 0;
    }

    """


class Paragraph(Block):
    """A paragraph Markdown block."""

    DEFAULT_CSS = """
    Markdown > Paragraph {
         margin: 0 0 1 0;
    }
    """


class BlockQuote(Block):
    """A block quote Markdown block."""

    DEFAULT_CSS = """
    BlockQuote {
        background: $boost;
        border-left: outer $success;
        margin: 1 0;
        padding: 0 1;
    }
    BlockQuote > BlockQuote {
        margin-left: 2;
        margin-top: 1;
    }

    """


class BulletList(Block):
    """A Bullet list Markdown block."""

    DEFAULT_CSS = """

    BulletList {
        margin: 0;
        padding: 0 0;
    }

    BulletList BulletList {
        margin: 0;
        padding-top: 0;
    }

    """


class OrderedList(Block):
    """An ordered list Markdown block."""

    DEFAULT_CSS = """

    OrderedList {
        margin: 0;
        padding: 0 0;
    }

    OrderedList OrderedList {
        margin: 0;
        padding-top: 0;
    }

    """


class Table(Block):
    """A Table markdown Block."""

    DEFAULT_CSS = """
    Table {
        margin: 1 0;
    }
    Table > DataTable {
        width: 100%;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        def flatten(block: Block) -> Iterable[Block]:
            for block in block.blocks:
                if block.blocks:
                    yield from flatten(block)
                yield block

        headers: list[Text] = []
        rows: list[list[Text]] = []
        for block in flatten(self):
            if isinstance(block, TH):
                headers.append(block.text)
            elif isinstance(block, TR):
                rows.append([])
            elif isinstance(block, TD):
                rows[-1].append(block.text)

        table: DataTable = DataTable(zebra_stripes=True, show_cursor=False)
        table.can_focus = False
        table.add_columns(*headers)
        table.add_rows([row for row in rows if row])
        yield table
        self.blocks.clear()


class TBody(Block):
    """A table body Markdown block."""

    DEFAULT_CSS = """

    """


class THead(Block):
    """A table head Markdown block."""

    DEFAULT_CSS = """

    """


class TR(Block):
    """A table row Markdown block."""

    DEFAULT_CSS = """

    """


class TH(Block):
    """A table header Markdown block."""

    DEFAULT_CSS = """

    """


class TD(Block):
    """A table data Markdown block."""

    DEFAULT_CSS = """

    """


class Bullet(Widget):
    """A bullet widget."""

    DEFAULT_CSS = """
    Bullet {
        width: auto;
    }
    """

    symbol = reactive("●​ ")

    def render(self) -> Text:
        return Text(self.symbol)


class ListItem(Block):
    """A list item Markdown block."""

    DEFAULT_CSS = """

    ListItem {
        layout: horizontal;
        margin-right: 1;
        height: auto;
    }

    ListItem > Vertical {
        width: 1fr;
        height: auto;
    }

    """

    def __init__(self, bullet: str) -> None:
        self.bullet = bullet
        super().__init__()

    def compose(self) -> ComposeResult:
        bullet = Bullet()
        bullet.symbol = self.bullet
        yield bullet
        yield Vertical(*self.blocks)

        self.blocks.clear()


class Fence(Block):
    """A fence Markdown block."""

    DEFAULT_CSS = """
    Fence {
        margin: 1 0;
        overflow: auto;
        width: 100%;
        height: auto;
        max-height: 20;
    }

    Fence > * {
        width: auto;
    }
    """

    def __init__(self, code: str, lexer: str) -> None:
        self.code = code
        self.lexer = lexer
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Static(
            Syntax(
                self.code,
                lexer=self.lexer,
                word_wrap=False,
                indent_guides=True,
                padding=(1, 2),
                theme="material",
            ),
            expand=True,
            shrink=False,
        )


HEADINGS = {"h1": H1, "h2": H2, "h3": H3, "h4": H4, "h5": H5, "h6": H6}

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

    def __init__(
        self,
        markdown: str | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        super().__init__(name=name, id=id, classes=classes)
        self._markdown = markdown

    class TOCUpdated(Message, bubble=True):
        """The table of contents was updated."""

        def __init__(self, toc: TOC, *, sender: Widget) -> None:
            super().__init__(sender=sender)
            self.toc = toc

    class TOCSelected(Message, bubble=True):
        """An item in the TOC was selected."""

        def __init__(self, block_id: str, *, sender: Widget) -> None:
            super().__init__(sender=sender)
            self.block_id = block_id

    class LinkClicked(Message, bubble=True):
        """A link in the document was clicked."""

        def __init__(self, href: str, *, sender: Widget) -> None:
            super().__init__(sender=sender)
            self.href: str = href
            """The link that was selected."""

    async def on_mount(self) -> None:
        if self._markdown is not None:
            await self.update(self._markdown)

    async def load(self, path: Path) -> bool:
        """Load a new Markdown document.

        Args:
            path: Path to the document.

        Returns:
            True    on success, or False if the document could not be read.
        """
        try:
            markdown = path.read_text(encoding="utf-8")
        except Exception:
            return False
        await self.query("Block").remove()
        await self.update(markdown)
        return True

    async def update(self, markdown: str) -> None:
        """Update the document with new Markdown.

        Args:
            markdown: A string containing Markdown.
        """
        output: list[Block] = []
        stack: list[Block] = []
        parser = MarkdownIt("gfm-like")

        content = Text()
        block_id: int = 0

        toc: TOC = []

        for token in parser.parse(markdown):
            if token.type == "heading_open":
                block_id += 1
                stack.append(HEADINGS[token.tag](id=f"block{block_id}"))
            elif token.type == "paragraph_open":
                stack.append(Paragraph())
            elif token.type == "blockquote_open":
                stack.append(BlockQuote())
            elif token.type == "bullet_list_open":
                stack.append(BulletList())
            elif token.type == "ordered_list_open":
                stack.append(OrderedList())
            elif token.type == "list_item_open":
                stack.append(ListItem(f"{token.info}. " if token.info else "● "))
            elif token.type == "table_open":
                stack.append(Table())
            elif token.type == "tbody_open":
                stack.append(TBody())
            elif token.type == "thead_open":
                stack.append(THead())
            elif token.type == "tr_open":
                stack.append(TR())
            elif token.type == "th_open":
                stack.append(TH())
            elif token.type == "td_open":
                stack.append(TD())
            elif token.type.endswith("_close"):
                block = stack.pop()
                if token.type == "heading_close":
                    heading = block.text.plain
                    level = int(token.tag[1:])
                    toc.append((level, heading, block.id))
                if stack:
                    stack[-1].blocks.append(block)
                else:
                    output.append(block)
            elif token.type == "inline":
                style_stack: list[Style] = [Style()]
                content = Text()
                if token.children:
                    for child in token.children:
                        if child.type == "text":
                            content.append(child.content, style_stack[-1])
                        elif child.type == "code_inline":
                            content.append(
                                child.content,
                                style_stack[-1]
                                + self.get_component_rich_style(
                                    "code_inline", partial=True
                                ),
                            )
                        elif child.type == "em_open":
                            style_stack.append(
                                style_stack[-1]
                                + self.get_component_rich_style("em", partial=True)
                            )
                        elif child.type == "strong_open":
                            style_stack.append(
                                style_stack[-1]
                                + self.get_component_rich_style("strong", partial=True)
                            )
                        elif child.type == "s_open":
                            style_stack.append(
                                style_stack[-1]
                                + self.get_component_rich_style("s", partial=True)
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

                stack[-1].set_content(content)
            elif token.type == "fence":
                output.append(
                    Fence(
                        token.content.rstrip(),
                        token.info,
                    )
                )

        await self.post_message(Markdown.TOCUpdated(toc, sender=self))
        await self.mount(*output)


class MarkdownTOC(Widget, can_focus_children=True):
    DEFAULT_CSS = """
    MarkdownTOC {
        width: auto;
        background: $panel;
        border-right: wide $background;
    }
    MarkdownTOC > Tree {
        padding: 1;
        width: auto;
    }
    """

    toc: reactive[TOC | None] = reactive(None, init=False)

    def compose(self) -> ComposeResult:
        tree: Tree = Tree("TOC")
        tree.show_root = False
        tree.show_guides = True
        tree.guide_depth = 4
        tree.auto_expand = False
        yield tree

    def watch_toc(self, toc: TOC) -> None:
        """Triggered when the TOC changes."""
        self.set_toc(toc)

    def set_toc(self, toc: TOC) -> None:
        """Set the Table of Contents.

        Args:
            toc: Table of contents.
        """
        tree = self.query_one(Tree)
        tree.clear()
        root = tree.root
        for level, name, block_id in toc:
            node = root
            for _ in range(level - 1):
                if node._children:
                    node = node._children[-1]
                    node.expand()
                    node.allow_expand = True
                else:
                    node = node.add(NUMERALS[level], expand=True)
            node.add_leaf(f"[dim]{NUMERALS[level]}[/] {name}", {"block_id": block_id})

    async def on_tree_node_selected(self, message: Tree.NodeSelected) -> None:
        node_data = message.node.data
        if node_data is not None:
            await self.post_message(
                Markdown.TOCSelected(node_data["block_id"], sender=self)
            )


class MarkdownViewer(Vertical, can_focus=True, can_focus_children=True):
    """A Markdown viewer widget."""

    DEFAULT_CSS = """
    MarkdownViewer {
        height: 1fr;
        scrollbar-gutter: stable;
    }

    MarkdownTOC {
        dock:left;
    }

    MarkdownViewer > MarkdownTOC {
        display: none;
    }

    MarkdownViewer.-show-toc > MarkdownTOC {
        display: block;
    }

    """

    show_toc = reactive(True)
    top_block = reactive("")

    navigator: var[Navigator] = var(Navigator)

    def __init__(
        self,
        markdown: str | None = None,
        *,
        show_toc: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        super().__init__(name=name, id=id, classes=classes)
        self.show_toc = show_toc
        self._markdown = markdown

    @property
    def document(self) -> Markdown:
        """The Markdown document object."""
        return self.query_one(Markdown)

    @property
    def toc(self) -> MarkdownTOC:
        """The Table of Contents widget"""
        return self.query_one(MarkdownTOC)

    async def on_mount(self) -> None:
        if self._markdown is not None:
            await self.document.update(self._markdown)

    async def go(self, location: str) -> bool:
        """Navigate to a new document path."""
        return await self.document.load(self.navigator.go(location))

    async def back(self) -> None:
        """Go back one level in the history."""
        if self.navigator.back():
            await self.document.load(self.navigator.location)

    async def forward(self) -> None:
        """Go forward one level in the history."""
        if self.navigator.forward():
            await self.document.load(self.navigator.location)

    async def on_markdown_link_clicked(self, message: Markdown.LinkClicked) -> None:
        message.stop()
        await self.go(message.href)

    def watch_show_toc(self, show_toc: bool) -> None:
        self.set_class(show_toc, "-show-toc")

    def compose(self) -> ComposeResult:
        yield MarkdownTOC()
        yield Markdown()

    def on_markdown_tocupdated(self, message: Markdown.TOCUpdated) -> None:
        self.query_one(MarkdownTOC).toc = message.toc
        message.stop()

    def on_markdown_tocselected(self, message: Markdown.TOCSelected) -> None:
        block_selector = f"#{message.block_id}"
        block = self.query_one(block_selector, Block)
        self.scroll_to_widget(block, top=True)
        message.stop()
