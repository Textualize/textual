from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Optional, Tuple

from rich.text import Text
from typing_extensions import TYPE_CHECKING

try:
    from tree_sitter_languages import get_language, get_parser

    if TYPE_CHECKING:
        from tree_sitter import Language, Parser, Tree
        from tree_sitter.binding import Query

    TREE_SITTER = True
except ImportError:
    TREE_SITTER = False

from textual._fix_direction import _fix_direction
from textual.document._document import Document, Location, _utf8_encode
from textual.document._languages import VALID_LANGUAGES
from textual.document._syntax_theme import SyntaxTheme

TREE_SITTER_PATH = Path(__file__) / "../../../../tree-sitter/"
HIGHLIGHTS_PATH = TREE_SITTER_PATH / "highlights/"

StartColumn = Optional[int]
EndColumn = Optional[int]
HighlightName = Optional[str]
Highlight = Tuple[StartColumn, EndColumn, HighlightName]


class SyntaxAwareDocument(Document):
    """A wrapper around a Document which also maintains a tree-sitter syntax
    tree when the document is edited.

    The primary reason for this split is actually to keep tree-sitter stuff separate,
    since it isn't supported in Python 3.7. By having the tree-sitter code
    isolated in this subclass, it makes it easier to conditionally import. However,
    it does come with other design flaws (e.g. Document is required to have methods
    which only really make sense on SyntaxAwareDocument).

    If you're reading this and Python 3.7 is no longer supported by Textual,
    consider merging this subclass into the `Document` superclass.
    """

    def __init__(
        self, text: str, language: str | Language, syntax_theme: str | SyntaxTheme
    ):
        super().__init__(text)
        self._language: Language | None = None
        """The tree-sitter Language or None if tree-sitter is unavailable."""

        self._parser: Parser | None = None
        """The tree-sitter Parser or None if tree-sitter is unavailable."""

        self._syntax_tree: Tree | None = None
        """The tree-sitter Tree (syntax tree) built from the document."""

        self._syntax_theme: SyntaxTheme | None = None
        """The syntax highlighting theme to use."""

        self._highlights: dict[int, list[Highlight]] = defaultdict(list)
        """Mapping line numbers to the set of highlights for that line."""

        if TREE_SITTER:
            if isinstance(language, str):
                if language not in VALID_LANGUAGES:
                    raise RuntimeError(f"Invalid language {language!r}")
                self._language = get_language(language)
                self._parser = get_parser(language)
            else:
                self._language = language
                self._parser = Parser()
                self._parser.set_language(language)

            highlight_query_path = (
                Path(HIGHLIGHTS_PATH.resolve()) / f"{self._language.name}.scm"
            )
            if isinstance(syntax_theme, SyntaxTheme):
                self._syntax_theme = syntax_theme
            else:
                self._syntax_theme = SyntaxTheme.get_theme(syntax_theme)

            self._syntax_theme.highlight_query = highlight_query_path.read_text()
            self._syntax_tree = self._build_ast(self._parser)
            self._query: Query = self._language.query(
                self._syntax_theme.highlight_query
            )
            self._prepare_highlights()

    def insert_range(
        self, start: tuple[int, int], end: tuple[int, int], text: str
    ) -> tuple[int, int]:
        """Insert text at the given range.

        Args:
            start: A tuple (row, column) where the edit starts.
            end: A tuple (row, column) where the edit ends.
            text: The text to insert between start and end.

        Returns:
            The new end location after the edit is complete.
        """
        top, bottom = _fix_direction(start, end)

        # An optimisation would be finding the byte offsets as a single operation rather
        # than doing two passes over the document content.
        start_byte = self._location_to_byte_offset(top)
        start_point = self._location_to_point(top)
        old_end_byte = self._location_to_byte_offset(bottom)
        old_end_point = self._location_to_point(bottom)

        end_location = super().insert_range(start, end, text)

        if TREE_SITTER:
            text_byte_length = len(_utf8_encode(text))
            self._syntax_tree.edit(
                start_byte=start_byte,
                old_end_byte=old_end_byte,
                new_end_byte=start_byte + text_byte_length,
                start_point=start_point,
                old_end_point=old_end_point,
                new_end_point=self._location_to_point(end_location),
            )
            self._syntax_tree = self._parser.parse(
                self._read_callable, self._syntax_tree
            )
            self._prepare_highlights()

        return end_location

    def delete_range(self, start: tuple[int, int], end: tuple[int, int]) -> str:
        """Delete text between `start` and `end`.

        This will update the internal syntax tree of the document, refreshing
        the syntax highlighting data. Calling `get_line` will now return a Text
        object with new highlights corresponding to this change.

        Args:
            start: The start of the range.
            end: The end of the range.

        Returns:
            A string containing the deleted text.
        """

        top, bottom = _fix_direction(start, end)
        start_point = self._location_to_point(top)
        old_end_point = self._location_to_point(bottom)
        start_byte = self._location_to_byte_offset(top)
        old_end_byte = self._location_to_byte_offset(bottom)

        deleted_text = super().delete_range(start, end)

        if TREE_SITTER:
            deleted_text_byte_length = len(_utf8_encode(deleted_text))
            self._syntax_tree.edit(
                start_byte=start_byte,
                old_end_byte=old_end_byte,
                new_end_byte=old_end_byte - deleted_text_byte_length,
                start_point=start_point,
                old_end_point=old_end_point,
                new_end_point=self._location_to_point(top),
            )
            new_tree = self._parser.parse(self._read_callable, self._syntax_tree)
            self._syntax_tree = new_tree
            self._prepare_highlights()

        return deleted_text

    def get_line_text(self, line_index: int) -> Text:
        """Apply syntax highlights and return the Text of the line.

        Args:
            line_index: The index of the line.

        Returns:
            The syntax highlighted Text of the line.
        """
        line_bytes = _utf8_encode(self[line_index])
        byte_to_codepoint = build_byte_to_codepoint_dict(line_bytes)
        line = Text(self[line_index], end="")
        if self._highlights:
            highlights = self._highlights[line_index]
            for start, end, highlight_name in highlights:
                node_style = self._syntax_theme.get_highlight(highlight_name)
                line.stylize(
                    node_style,
                    byte_to_codepoint.get(start, 0),
                    byte_to_codepoint.get(end),
                )

        return line

    def tree_query(self, tree_query: str) -> list[object]:
        """Query the syntax tree."""
        query = self._language.query(tree_query)

        captures = query.captures(self._syntax_tree.root_node)

        return list(captures)

    def _location_to_byte_offset(self, location: tuple[int, int]) -> int:
        """Given a document coordinate, return the byte offset of that coordinate.
        This method only does work if tree-sitter was imported, otherwise it returns 0.

        Args:
            location: The location to convert.

        Returns:
            An integer byte offset for the given location.
        """
        if not TREE_SITTER:
            return 0

        lines = self._lines
        row, column = location
        lines_above = lines[:row]
        end_of_line_width = len(self.newline)
        bytes_lines_above = sum(
            len(_utf8_encode(line)) + end_of_line_width for line in lines_above
        )
        if row < len(lines):
            bytes_on_left = len(_utf8_encode(lines[row][:column]))
        else:
            bytes_on_left = 0
        byte_offset = bytes_lines_above + bytes_on_left
        return byte_offset

    def _location_to_point(self, location: Location) -> tuple[int, int]:
        """Convert a document location (row_index, column_index) to a tree-sitter
        point (row_index, byte_offset_from_start_of_row)."""
        lines = self._lines
        row, column = location
        if row < len(lines):
            bytes_on_left = len(_utf8_encode(lines[row][:column]))
        else:
            bytes_on_left = 0
        return row, bytes_on_left

    def _prepare_highlights(
        self,
        start_point: tuple[int, int] | None = None,
        end_point: tuple[int, int] = None,
    ) -> None:
        """Query the tree for ranges to highlights, and update the internal highlights mapping.

        Args:
            start_point: The point to start looking for highlights from.
            end_point: The point to look for highlights to.
        """
        if not TREE_SITTER:
            return None

        highlights = self._highlights

        captures_kwargs = {}
        if start_point is not None:
            captures_kwargs["start_point"] = start_point
        if end_point is not None:
            captures_kwargs["end_point"] = end_point

        # We could optimise by only preparing highlights for a subset of lines here.
        captures = self._query.captures(self._syntax_tree.root_node, **captures_kwargs)

        highlight_updates: dict[int, list[Highlight]] = defaultdict(list)
        for capture in captures:
            node, highlight_name = capture
            node_start_row, node_start_column = node.start_point
            node_end_row, node_end_column = node.end_point

            if node_start_row == node_end_row:
                highlight = (node_start_column, node_end_column, highlight_name)
                highlight_updates[node_start_row].append(highlight)
            else:
                # Add the first line of the node range
                highlight_updates[node_start_row].append(
                    (node_start_column, None, highlight_name)
                )

                # Add the middle lines - entire row of this node is highlighted
                for node_row in range(node_start_row + 1, node_end_row):
                    highlight_updates[node_row].append((0, None, highlight_name))

                # Add the last line of the node range
                highlight_updates[node_end_row].append(
                    (0, node_end_column, highlight_name)
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
        newline = self.newline

        row_out_of_bounds = row >= len(lines)
        if row_out_of_bounds:
            return None
        else:
            row_text = lines[row]

        encoded_row = _utf8_encode(row_text)
        encoded_row_length = len(encoded_row)

        if column < encoded_row_length:
            return encoded_row[column:] + _utf8_encode(newline)
        elif column == encoded_row_length:
            return _utf8_encode(newline[0])
        elif column == encoded_row_length + 1:
            if newline == "\r\n":
                return b"\n"
        else:
            return None


@lru_cache(maxsize=128)
def build_byte_to_codepoint_dict(data: bytes) -> dict[int, int]:
    byte_to_codepoint = {}
    current_byte_offset = 0
    code_point_offset = 0

    while current_byte_offset < len(data):
        # Save the mapping before incrementing the byte offset
        byte_to_codepoint[current_byte_offset] = code_point_offset

        first_byte = data[current_byte_offset]

        # Single-byte character
        if (first_byte & 0b10000000) == 0:
            current_byte_offset += 1
        # 2-byte character
        elif (first_byte & 0b11100000) == 0b11000000:
            current_byte_offset += 2
        # 3-byte character
        elif (first_byte & 0b11110000) == 0b11100000:
            current_byte_offset += 3
        # 4-byte character
        elif (first_byte & 0b11111000) == 0b11110000:
            current_byte_offset += 4
        else:
            raise ValueError(f"Invalid UTF-8 byte: {first_byte}")

        # Increment the code-point counter
        code_point_offset += 1

    # Mapping for the end of the string
    byte_to_codepoint[current_byte_offset] = code_point_offset

    return byte_to_codepoint
