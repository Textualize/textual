from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Iterable

from rich.segment import Segment
from rich.style import Style
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


class TextEditor(ScrollView, can_focus=True):
    BINDINGS = [
        Binding("ctrl+l", "print_line_cache", "[debug] Line Cache"),
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
            if row >= len(document_lines) or column >= len(document_lines[row]):
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

        # Fetch the segments from the cache
        strip = Strip(self._line_cache.get(document_y, Strip.blank(self.size.width)))
        return strip

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
        # The range of the document (line indices) that we want to highlight.
        if line_range is not None:
            window_start, window_end = line_range
        else:
            window_start = 0
            window_end = len(document) - 1

        # Get the range of this node
        node_start_line = cursor.node.start_point[0]
        node_end_line = cursor.node.end_point[0]

        node_in_window = line_range is None or (
            window_start <= node_end_line and window_end >= node_start_line
        )

    # Apply simple highlighting to the node based on its type.
    # if cursor.node.type == 'identifier':
    #     style = Style(color="black", bgcolor="red")
    # elif cursor.node.type == 'string':
    #     style = Style(color="green", italic=True)
    # else:
    #     style = Style.null()

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


if __name__ == "__main__":
    pass
# Language.build_library(
#     '../../../tree-sitter-languages/textual-languages.so',
#     [
#         'tree-sitter-libraries/tree-sitter-python'
#     ]
# )
