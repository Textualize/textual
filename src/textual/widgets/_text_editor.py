from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Iterable, NamedTuple

from rich.segment import Segment
from rich.style import Style
from rich.text import Text
from tree_sitter import Language, Node, Parser, Tree

from textual import log
from textual._cells import cell_len
from textual.binding import Binding
from textual.geometry import Size
from textual.reactive import Reactive, reactive
from textual.scroll_view import ScrollView
from textual.strip import Strip

LANGUAGES_PATH = (
    Path(__file__) / "../../../../tree-sitter-languages/textual-languages.so"
)


class Highlight(NamedTuple):
    """A range to highlight within a single line"""

    start_column: int | None
    end_column: int | None
    node_type: str


class TextEditor(ScrollView, can_focus=True):
    BINDINGS = [
        Binding("ctrl+s", "print_highlight_cache", "[debug] Print highlight cache"),
        Binding("ctrl+l", "print_line_cache", "[debug] Print line cache"),
    ]

    language: Reactive[str | None] = reactive(None)
    """The language to use for syntax highlighting (via tree-sitter)."""
    cursor_position = reactive((0, 0))
    """The cursor position (zero-based line_index, offset)."""

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

        # --- Core editor data
        self.document_lines: list[str] = []
        """Each string in this list represents a line in the document."""

        self._highlights: dict[int, set[Highlight]] = defaultdict(set)
        """Mapping line numbers to the set of cached highlights for that line."""

        # TODO - currently unused
        self._line_cache: dict[int, list[Segment]] = defaultdict(list)
        """Caches segments for lines. Note that a line may span multiple y-offsets
         due to wrapping. These segments do NOT include the cursor highlighting.
         A portion of the line cache will be updated when an edit operation occurs
         or when a file is loaded for the first time.
         Tree sitter will tell us the modified ranges of the AST and we update
         the corresponding line ranges in this cache."""

        # --- Abstract syntax tree and related parsing machinery
        self._parser: Parser | None = None
        """The tree-sitter parser which extracts the syntax tree from the document."""
        self._ast: Tree | None = None
        """The tree-sitter Tree (AST) built from the document."""

    def watch_language(self, new_language: str | None) -> None:
        """Update the language used in AST parsing.

        When the language reactive string is updated, fetch the Language definition
        from our tree-sitter library file. If the language reactive is set to None,
        then the no parser is used."""
        if new_language:
            language = Language(LANGUAGES_PATH.resolve(), new_language)
            parser = Parser()
            self._parser = parser
            self._parser.set_language(language)
            self._ast = self._build_ast(parser, self.document_lines)
        else:
            self._ast = None

        log.debug(f"parser set to {self._parser}")

    def _build_ast(
        self,
        parser: Parser,
        document_lines: list[str],
    ) -> Tree | None:
        """Fully parse the document and build the abstract syntax tree for it.

        Returns None if there's no parser available (e.g. when no language is selected).
        """

        def read_callable(byte_offset, point):
            row, column = point
            row_out_of_bounds = row >= len(document_lines)
            column_out_of_bounds = not row_out_of_bounds and column >= len(
                document_lines[row]
            )
            if row_out_of_bounds or column_out_of_bounds:
                return None
            return document_lines[row][column:].encode("utf8")

        if parser:
            return parser.parse(read_callable)
        else:
            return None

    def load_text(self, text: str) -> None:
        """Load text from a string into the editor."""
        lines = text.splitlines(keepends=True)
        self.load_lines(lines)

    def load_lines(self, lines: list[str]) -> None:
        """Load text from a list of lines into the editor."""
        self.document_lines = lines

        # TODO Offer maximum line width and wrap if needed
        width = max(cell_len(line) for line in lines)
        height = len(lines)
        self.virtual_size = Size(width, height)

        # TODO - clear caches
        if self._parser is not None:
            self._ast = self._build_ast(self._parser, lines)
            self._cache_highlights(self._ast.walk(), lines)

        log.debug(f"loaded text. parser = {self._parser} ast = {self._ast}")

    def render_line(self, widget_y: int) -> Strip:
        document_lines = self.document_lines

        document_y = round(self.scroll_y + widget_y)
        out_of_bounds = document_y >= len(document_lines)
        if out_of_bounds:
            return Strip.blank(self.size.width)

        line_string = document_lines[document_y].replace("\n", "").replace("\r", "")
        line_text = Text(line_string, end="")

        # Apply highlighting to the line if necessary.
        if self._highlights:
            highlights = self._highlights[document_y]
            for start, end, node_type in highlights:
                node_style = self._get_node_style(node_type)
                line_text.stylize(node_style, start, end)

        # We need to render according to the virtual size otherwise the rendering
        # will wrap the text content incorrectly.
        segments = self.app.console.render(
            line_text, self.app.console.options.update_width(self.virtual_size.width)
        )
        strip = (
            Strip(segments)
            .adjust_cell_length(self.virtual_size.width)
            .crop(int(self.scroll_x), int(self.scroll_x) + self.virtual_size.width)
            .simplify()
        )
        log.debug(f"{document_y}|{repr(strip.text)}|")

        return strip

    def _get_node_style(self, node_type: str) -> Style:
        # Apply simple highlighting to the node based on its type.
        if node_type == "identifier":
            style = Style(color="cyan")
        elif node_type == "string":
            style = Style(color="green")
        elif node_type == "import_from_statement":
            style = Style(bgcolor="magenta")
        else:
            style = Style.null()
        return style

    def _cache_highlights(
        self,
        cursor,
        document: list[str],
        line_range: tuple[int, int] | None = None,
    ) -> None:
        """Traverse the AST and highlight the document.

        Args:
            cursor: The tree-sitter Tree cursor.
            document: The document as a list of strings.
            line_range: The start and end line index that is visible. If None, highlight the whole document.
        """

        reached_root = False

        while not reached_root:
            # The range of the document (line indices) that we want to highlight.
            if line_range is not None:
                window_start, window_end = line_range
            else:
                window_start = 0
                window_end = len(document) - 1

            # Get the range of this node
            node_start_row, node_start_column = cursor.node.start_point
            node_end_row, node_end_column = cursor.node.end_point

            node_in_window = line_range is None or (
                window_start <= node_end_row and window_end >= node_start_row
            )

            # Cache the highlight data for this node if it's within the window range
            # At this point we're not actually looking at the document at all, we're
            # just storing data on the locations to highlight within the document.
            # This data will be referenced only when we render.
            log.debug(f"Processing highlights for node {cursor.node}")

            if node_in_window:
                highlight_cache = self._highlights
                node_type = cursor.node.type
                if node_start_row == node_end_row:
                    highlight = Highlight(node_start_column, node_end_column, node_type)
                    highlight_cache[node_start_row].add(highlight)
                else:
                    # Add the first line
                    highlight_cache[node_start_row].add(
                        Highlight(node_start_column, None, node_type)
                    )
                    # Add the middle lines - entire row of this node is highlighted
                    for node_row in range(node_start_row + 1, node_end_row):
                        highlight_cache[node_row].add(Highlight(0, None, node_type))

                    # Add the last line
                    highlight_cache[node_end_row].add(
                        Highlight(0, node_end_column, node_type)
                    )

            if cursor.goto_first_child():
                continue

            if cursor.goto_next_sibling():
                continue

            retracing = True
            while retracing:
                if not cursor.goto_parent():
                    retracing = False
                    reached_root = True

                if cursor.goto_next_sibling():
                    retracing = False

    def action_print_line_cache(self) -> None:
        log.debug(self._line_cache)

        # TODO - this traversal is correct - see notes in Notion
        def traverse(cursor) -> Iterable[Node]:
            yield cursor.node

            if cursor.goto_first_child():
                yield from traverse(cursor)
                while cursor.goto_next_sibling():
                    yield from traverse(cursor)
                cursor.goto_parent()

        log.debug(list(traverse(self._ast.walk())))

    def action_print_highlight_cache(self) -> None:
        log.debug(self._highlights)


if __name__ == "__main__":

    def traverse_tree(cursor):
        reached_root = False
        while reached_root == False:
            yield cursor.node

            if cursor.goto_first_child():
                continue

            if cursor.goto_next_sibling():
                continue

            retracing = True
            while retracing:
                if not cursor.goto_parent():
                    retracing = False
                    reached_root = True

                if cursor.goto_next_sibling():
                    retracing = False

    language = Language(LANGUAGES_PATH.resolve(), "python")
    parser = Parser()
    parser.set_language(language)

    CODE = """\
    from textual.app import App


    class ScreenApp(App):
        def on_mount(self) -> None:
            self.screen.styles.background = "darkblue"
            self.screen.styles.border = ("heavy", "white")


    if __name__ == "__main__":
        app = ScreenApp()
        app.run()
    """

    document_lines = CODE.splitlines(keepends=False)

    def read_callable(byte_offset, point):
        row, column = point
        if row >= len(document_lines) or column >= len(document_lines[row]):
            return None
        return document_lines[row][column:].encode("utf8")

    tree = parser.parse(bytes(CODE, "utf-8"))

    print(list(traverse_tree(tree.walk())))
