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

from textual._fix_direction import _sort_ascending
from textual.document._document import Document, EditResult, Location, _utf8_encode
from textual.document._languages import VALID_LANGUAGES
from textual.document._syntax_theme import SyntaxTheme

TREE_SITTER_PATH = Path(__file__) / "../../../../tree-sitter/"
HIGHLIGHTS_PATH = TREE_SITTER_PATH / "highlights/"

StartColumn = int
EndColumn = Optional[int]
HighlightName = str
Highlight = Tuple[StartColumn, EndColumn, HighlightName]
"""A tuple representing a syntax highlight within one line."""


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
        """Construct a SyntaxAwareDocument.

        Args:
            text: The initial text contained in the document.
            language: The language to use. You can pass a string to use a supported
                language, or pass in your own tree-sitter `Language` object.
            syntax_theme: The syntax highlighting theme to use. You can pass a string
                to use a builtin theme,  or construct your own custom SyntaxTheme and
                provide that.
        """
        if not TREE_SITTER:
            raise RuntimeError("SyntaxAwareDocument is unavailable on Python 3.7.")

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
            self._syntax_tree = self._parser.parse(self._read_callable)  # type: ignore
            self._query: Query = self._language.query(
                self._syntax_theme.highlight_query
            )
            self._prepare_highlights()

    def replace_range(self, start: Location, end: Location, text: str) -> EditResult:
        """Replace text at the given range.

        Args:
            start: A tuple (row, column) where the edit starts.
            end: A tuple (row, column) where the edit ends.
            text: The text to insert between start and end.

        Returns:
            The new end location after the edit is complete.
        """
        top, bottom = _sort_ascending(start, end)

        # An optimisation would be finding the byte offsets as a single operation rather
        # than doing two passes over the document content.
        start_byte = self._location_to_byte_offset(top)
        start_point = self._location_to_point(top)
        old_end_byte = self._location_to_byte_offset(bottom)
        old_end_point = self._location_to_point(bottom)

        replace_result = super().replace_range(start, end, text)

        if TREE_SITTER:
            text_byte_length = len(_utf8_encode(text))
            end_location = replace_result.end_location
            assert self._syntax_tree is not None
            assert self._parser is not None
            self._syntax_tree.edit(
                start_byte=start_byte,
                old_end_byte=old_end_byte,
                new_end_byte=start_byte + text_byte_length,
                start_point=start_point,
                old_end_point=old_end_point,
                new_end_point=self._location_to_point(end_location),
            )
            # Incrementally parse the document.
            self._syntax_tree = self._parser.parse(
                self._read_callable, self._syntax_tree  # type: ignore[arg-type]
            )
            self._prepare_highlights()

        return replace_result

    def get_line_text(self, line_index: int) -> Text:
        """Apply syntax highlights and return the Text of the line.

        Args:
            line_index: The index of the line.

        Returns:
            The syntax highlighted Text of the line.
        """
        line_string = self[line_index]
        line = Text(line_string, end="")
        if not TREE_SITTER or self._syntax_theme is None:
            return line

        highlights = self._highlights
        if highlights:
            line_bytes = _utf8_encode(line_string)
            byte_to_codepoint = build_byte_to_codepoint_dict(line_bytes)
            get_highlight_from_theme = self._syntax_theme.get_highlight
            line_highlights = highlights[line_index]
            for start, end, highlight_name in line_highlights:
                node_style = get_highlight_from_theme(highlight_name)
                line.stylize(
                    node_style,
                    byte_to_codepoint.get(start, 0),
                    byte_to_codepoint.get(end) if end else None,
                )
        return line

    def _location_to_byte_offset(self, location: Location) -> int:
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
        point (row_index, byte_offset_from_start_of_row). If tree-sitter isn't available
        returns (0, 0).

        Args:
            location: A location (row index, column codepoint offset)

        Returns:
            The point corresponding to that location (row index, column byte offset).
        """
        if not TREE_SITTER:
            return 0, 0

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
        end_point: tuple[int, int] | None = None,
    ) -> None:
        """Query the tree for ranges to highlights, and update the internal highlights mapping.

        Args:
            start_point: The point to start looking for highlights from.
            end_point: The point to look for highlights to.
        """
        if not TREE_SITTER:
            return None

        assert self._syntax_tree is not None

        highlights = self._highlights
        highlights.clear()

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

    def _read_callable(self, byte_offset: int, point: tuple[int, int]) -> bytes:
        """A callable which informs tree-sitter about the document content.

        This is passed to tree-sitter which will call it frequently to retrieve
        the bytes from the document.

        Args:
            byte_offset: The number of (utf-8) bytes from the start of the document.
            point: A tuple (row index, column *byte* offset). Note that this differs
                from our Location tuple which is (row_index, column codepoint offset).

        Returns:
            All the utf-8 bytes between the byte_offset/point and the end of the current
                line _including_ the line separator character(s). Returns None if the
                offset/point requested by tree-sitter doesn't correspond to a byte.
        """
        row, column = point
        lines = self._lines
        newline = self.newline

        row_out_of_bounds = row >= len(lines)
        if row_out_of_bounds:
            return b""
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

        return b""


@lru_cache(maxsize=128)
def build_byte_to_codepoint_dict(data: bytes) -> dict[int, int]:
    """Build a mapping of utf-8 byte offsets to codepoint offsets for the given data.

    Args:
        data: utf-8 bytes.

    Returns:
        A `dict[int, int]` mapping byte indices to codepoint indices within `data`.
    """
    byte_to_codepoint = {}
    current_byte_offset = 0
    code_point_offset = 0

    while current_byte_offset < len(data):
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

        code_point_offset += 1

    # Mapping for the end of the string
    byte_to_codepoint[current_byte_offset] = code_point_offset
    return byte_to_codepoint
