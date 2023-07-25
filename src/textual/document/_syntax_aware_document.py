from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import NamedTuple

from rich.style import Style
from rich.text import Text
from tree_sitter import Language, Parser, Tree
from tree_sitter.binding import Query

from textual import log
from textual.document._document import Document

# TODO - remove hardcoded python.scm highlight query file
TREE_SITTER_PATH = Path(__file__) / "../../../../tree-sitter/"
LANGUAGES_PATH = TREE_SITTER_PATH / "textual-languages.so"
HIGHLIGHTS_PATH = TREE_SITTER_PATH / "highlights/python.scm"

HIGHLIGHT_STYLES = {
    "string": Style(color="#E6DB74"),
    "string.documentation": Style(color="yellow"),
    "comment": Style(color="#75715E"),
    "keyword": Style(color="#F92672"),
    "include": Style(color="#F92672"),
    "keyword.function": Style(color="#F92672"),
    "keyword.return": Style(color="#F92672"),
    "conditional": Style(color="#F92672"),
    "number": Style(color="#AE81FF"),
    "class": Style(color="#A6E22E"),
    "function": Style(color="#A6E22E"),
    "function.call": Style(color="#A6E22E"),
    "method": Style(color="#A6E22E"),
    "method.call": Style(color="#A6E22E"),
    # "constant": Style(color="#AE81FF"),
    "variable": Style(color="white"),
    "parameter": Style(color="cyan"),
    "type": Style(color="cyan"),
    "escape": Style(bgcolor="magenta"),
}


class Highlight(NamedTuple):
    """A range to highlight within a single line"""

    start_column: int | None
    end_column: int | None
    highlight_name: str | None


class SyntaxAwareDocument(Document):
    def __init__(self, language: str | None = None):
        super().__init__()

        # TODO validate language string

        self._language: Language = Language(LANGUAGES_PATH.resolve(), language)
        """The tree-sitter Language."""

        self._parser: Parser = Parser()
        """The tree-sitter Parser"""
        self._parser.set_language(self._language)

        self._syntax_tree = self._build_ast(self._parser)
        """The tree-sitter Tree (syntax tree) built from the document."""

        self._highlights_query = Path(HIGHLIGHTS_PATH.resolve()).read_text()
        """The tree-sitter query string for used to fetch highlighted ranges"""

        self._highlights: dict[int, list[Highlight]] = defaultdict(list)
        """Mapping line numbers to the set of cached highlights for that line."""

    def load_text(self, text: str) -> None:
        super().load_text(text)
        self._build_ast(self._parser)
        self._prepare_highlights()

    def insert_range(
        self, start: tuple[int, int], end: tuple[int, int], text: str
    ) -> tuple[int, int]:
        end_location = super().insert_range(start, end, text)

    def delete_range(self, start: tuple[int, int], end: tuple[int, int]) -> str:
        deleted_text = super().delete_range(start, end)

        # TODO - apply edits to the ast

    def _prepare_highlights(
        self,
        start_point: tuple[int, int] | None = None,
        end_point: tuple[int, int] = None,
    ) -> None:
        # TODO - we're ignoring get changed ranges for now. Either I'm misunderstanding
        #  it or I've made a mistake somewhere with AST editing.

        highlights = self._highlights
        query: Query = self._language.query(self._highlights_query)

        log.debug(f"capturing nodes in range {start_point!r} -> {end_point!r}")

        captures_kwargs = {}
        if start_point is not None:
            captures_kwargs["start_point"] = start_point
        if end_point is not None:
            captures_kwargs["end_point"] = end_point

        captures = query.captures(self._syntax_tree.root_node, **captures_kwargs)

        highlight_updates: dict[int, list[Highlight]] = defaultdict(list)
        for capture in captures:
            node, highlight_name = capture
            node_start_row, node_start_column = node.start_point
            node_end_row, node_end_column = node.end_point

            if node_start_row == node_end_row:
                highlight = Highlight(
                    node_start_column, node_end_column, highlight_name
                )
                highlight_updates[node_start_row].append(highlight)
            else:
                # Add the first line
                highlight_updates[node_start_row].append(
                    Highlight(node_start_column, None, highlight_name)
                )
                # Add the middle lines - entire row of this node is highlighted
                for node_row in range(node_start_row + 1, node_end_row):
                    highlight_updates[node_row].append(
                        Highlight(0, None, highlight_name)
                    )

                # Add the last line
                highlight_updates[node_end_row].append(
                    Highlight(0, node_end_column, highlight_name)
                )

        for line_index, updated_highlights in highlight_updates.items():
            highlights[line_index] = updated_highlights

    def _build_ast(
        self,
        parser: Parser,
    ) -> Tree | None:
        """Fully parse the document and build the abstract syntax tree for it.

        Returns None if there's no parser available (e.g. when no language is selected).
        """
        if parser:
            return parser.parse(self._read_callable)
        else:
            return None

    def _read_callable(self, byte_offset: int, point: tuple[int, int]) -> bytes | None:
        row, column = point
        lines = self._lines

        row_out_of_bounds = row >= len(lines)
        column_out_of_bounds = not row_out_of_bounds and column > len(lines[row])

        if row_out_of_bounds or column_out_of_bounds:
            return_value = None
        elif column == len(lines[row]) and row < len(lines):
            return_value = "\n".encode("utf8")
        else:
            return_value = lines[row][column].encode("utf8")

        return return_value

    def get_line(self, line_index: int) -> Text:
        null_style = Style.null()
        line = Text(self[line_index])

        if self._highlights:
            highlights = self._highlights[line_index]
            for start, end, highlight_name in highlights:
                node_style = HIGHLIGHT_STYLES.get(highlight_name, null_style)
                line.stylize(node_style, start, end)

        return line
