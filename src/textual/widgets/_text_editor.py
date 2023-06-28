from __future__ import annotations

from pathlib import Path

from rich.segment import Segment
from tree_sitter import Language, Parser

from textual._cells import cell_len
from textual.geometry import Size
from textual.reactive import Reactive, reactive
from textual.scroll_view import ScrollView
from textual.strip import Strip

LANGUAGES_PATH = (
    Path(__file__) / "../../../../tree-sitter-languages/textual-languages.so"
)


class TextEditor(ScrollView):
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
        self.parser: Parser | None = None
        """The tree-sitter parser which extracts the syntax tree from the document."""
        self.document_lines: list[str] = []
        """Each string in this list represents a line in the document."""

    def watch_language(self, new_language: str | None) -> None:
        """Update the language used in AST parsing.

        When the language reactive string is updated, fetch the Language definition
        from our tree-sitter library file. If the language reactive is set to None,
        then the no parser is used."""
        if new_language:
            language = Language(LANGUAGES_PATH.resolve(), new_language)
            parser = Parser()
            parser.set_language(language)
            self.parser = parser
        else:
            self.parser = None

    def load_text(self, text: str) -> None:
        """Load text from a string into the editor."""
        lines = text.splitlines(keepends=False)
        self.load_lines(lines)

    def load_lines(self, lines: list[str]) -> None:
        """Load text from a list of lines into the editor."""
        self.document_lines = lines

        # TODO Offer maximum line width and wrap if needed
        width = max(cell_len(line) for line in lines)
        height = len(lines)
        self.virtual_size = Size(width, height)

    def render_line(self, widget_y: int) -> Strip:
        document_lines = self.document_lines

        document_y = round(self.scroll_y + widget_y)
        out_of_bounds = document_y >= len(document_lines)
        if out_of_bounds:
            return Strip.blank(self.size.width)

        # TODO For now, we naively just pull the line from the document based on
        #  y_offset. This will later need to be adjusted to account for wrapping.
        line = document_lines[document_y]
        return Strip([Segment(line)], cell_len(line))


if __name__ == "__main__":
    # Language.build_library(
    #     '../../../tree-sitter-languages/textual-languages.so',
    #     [
    #         'tree-sitter-libraries/tree-sitter-python'
    #     ]
    # )
    this_directory = Path(__file__).parent
    languages = this_directory / "../../../tree-sitter-languages/textual-languages.so"
    python_language = Language(languages.resolve(), "python")

    parser = Parser()
    parser.set_language(python_language)

    tree = parser.parse(
        bytes(
            """\
    def foo():
        if bar:
            baz()
    """,
            "utf8",
        )
    )

    def traverse(cursor):
        # Start with the first child
        if cursor.goto_first_child():
            print(cursor.node)
            traverse(cursor)

            # Continue with the siblings
            while cursor.goto_next_sibling():
                print(cursor.node)
                traverse(cursor)

            # Go back up to the parent when done
            cursor.goto_parent()

    # Start traversal with the root of the tree
    traverse(tree.walk())
