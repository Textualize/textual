from __future__ import annotations

from pathlib import Path

from rich.segment import Segment
from tree_sitter import Language, Parser

from textual._cells import cell_len
from textual.reactive import Reactive, reactive
from textual.scroll_view import ScrollView
from textual.strip import Strip

LANGUAGES_PATH = Path(__file__) / "../../../tree-sitter-languages/textual-languages.so"
SAMPLE_TEXT = [
    "Hello, world!",
    "",
    "你好，世界！",  # Chinese characters, which are usually double-width
    "こんにちは、世界！",  # Japanese characters, also usually double-width
    "안녕하세요, 세계!",  # Korean characters, also usually double-width
    "    This line has leading white space",
    "This line has trailing white space    ",
    "    This line has both leading and trailing white space    ",
    "    ",  # Line with only spaces
    "こんにちは、world! 你好，world!",  # Mixed script line
    "Hello, 🌍! Hello, 🌏! Hello, 🌎!",  # Line with emoji (which are often double-width)
    "The quick brown 🦊 jumps over the lazy 🐶.",  # Line with emoji interspersed in text
    "Special characters: ~!@#$%^&*()_+`-={}|[]\\:\";'<>?,./",
    # Line with special characters
    "Unicode example: Привет, мир!",  # Russian text
    "Unicode example: Γειά σου Κόσμε!",  # Greek text
    "Unicode example: مرحبا بك في",  # Arabic text
]


class TextArea(ScrollView):
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
        self.document_lines: list[str] = SAMPLE_TEXT.copy()
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
