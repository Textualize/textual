from __future__ import annotations

from pathlib import Path

from tree_sitter import Language, Parser

from textual.strip import Strip
from textual.widget import Widget


class TextArea(Widget):
    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

        # Load the tree-sitter libraries

    def render_line(self, y: int) -> Strip:
        pass


if __name__ == "__main__":
    # Language.build_library(
    #     '../../../build/textual-languages.so',
    #     [
    #         'tree-sitter-libraries/tree-sitter-python'
    #     ]
    # )
    this_directory = Path(__file__).parent
    languages = this_directory / "../../../build/textual-languages.so"
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
