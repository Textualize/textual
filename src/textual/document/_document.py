from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import lru_cache
from typing import TYPE_CHECKING, NamedTuple, Tuple, overload

from typing_extensions import Literal, get_args

if TYPE_CHECKING:
    from tree_sitter import Node
    from tree_sitter.binding import Query

from textual._cells import cell_len
from textual.geometry import Size

Newline = Literal["\r\n", "\n", "\r"]
"""The type representing valid line separators."""
VALID_NEWLINES = set(get_args(Newline))
"""The set of valid line separator strings."""


@dataclass
class EditResult:
    """Contains information about an edit that has occurred."""

    end_location: Location
    """The new end Location after the edit is complete."""
    replaced_text: str
    """The text that was replaced."""


@lru_cache(maxsize=1024)
def _utf8_encode(text: str) -> bytes:
    """Encode the input text as utf-8 bytes.

    The returned encoded bytes may be retrieved from a cache.

    Args:
        text: The text to encode.

    Returns:
        The utf-8 bytes representing the input string.
    """
    return text.encode("utf-8")


def _detect_newline_style(text: str) -> Newline:
    """Return the newline type used in this document.

    Args:
        text: The text to inspect.

    Returns:
        The Newline used in the file.
    """
    if "\r\n" in text:  # Windows newline
        return "\r\n"
    elif "\n" in text:  # Unix/Linux/MacOS newline
        return "\n"
    elif "\r" in text:  # Old MacOS newline
        return "\r"
    else:
        return "\n"  # Default to Unix style newline


class DocumentBase(ABC):
    """Describes the minimum functionality a Document implementation must
    provide in order to be used by the TextArea widget."""

    @abstractmethod
    def replace_range(self, start: Location, end: Location, text: str) -> EditResult:
        """Replace the text at the given range.

        Args:
            start: A tuple (row, column) where the edit starts.
            end: A tuple (row, column) where the edit ends.
            text: The text to insert between start and end.

        Returns:
            The new end location after the edit is complete.
        """

    @property
    @abstractmethod
    def text(self) -> str:
        """The text from the document as a string."""

    @property
    @abstractmethod
    def newline(self) -> Newline:
        """Return the line separator used in the document."""

    @property
    @abstractmethod
    def lines(self) -> list[str]:
        """Get the lines of the document as a list of strings.

        The strings should *not* include newline characters. The newline
        character used for the document can be retrieved via the newline
        property.
        """

    @abstractmethod
    def get_line(self, index: int) -> str:
        """Returns the line with the given index from the document.

        This is used in rendering lines, and will be called by the
        TextArea for each line that is rendered.

        Args:
            index: The index of the line in the document.

        Returns:
            The str instance representing the line.
        """

    @abstractmethod
    def get_text_range(self, start: Location, end: Location) -> str:
        """Get the text that falls between the start and end locations.

        Args:
            start: The start location of the selection.
            end: The end location of the selection.

        Returns:
            The text between start (inclusive) and end (exclusive).
        """

    @abstractmethod
    def get_size(self, indent_width: int) -> Size:
        """Get the size of the document.

        The height is generally the number of lines, and the width
        is generally the maximum cell length of all the lines.

        Args:
            indent_width: The width to use for tab characters.

        Returns:
            The Size of the document bounding box.
        """

    def query_syntax_tree(
        self,
        query: Query,
        start_point: tuple[int, int] | None = None,
        end_point: tuple[int, int] | None = None,
    ) -> list[tuple[Node, str]]:
        """Query the tree-sitter syntax tree.

        The default implementation always returns an empty list.

        To support querying in a subclass, this must be implemented.

        Args:
            query: The tree-sitter Query to perform.
            start_point: The (row, column byte) to start the query at.
            end_point: The (row, column byte) to end the query at.

        Returns:
            A tuple containing the nodes and text captured by the query.
        """
        return []

    def prepare_query(self, query: str) -> Query | None:
        return None

    @property
    @abstractmethod
    def line_count(self) -> int:
        """Returns the number of lines in the document."""

    @property
    @abstractmethod
    def start(self) -> Location:
        """Returns the location of the start of the document (0, 0)."""
        return (0, 0)

    @property
    @abstractmethod
    def end(self) -> Location:
        """Returns the location of the end of the document."""

    @overload
    def __getitem__(self, line_index: int) -> str: ...

    @overload
    def __getitem__(self, line_index: slice) -> list[str]: ...

    @abstractmethod
    def __getitem__(self, line_index: int | slice) -> str | list[str]:
        """Return the content of a line as a string, excluding newline characters.

        Args:
            line_index: The index or slice of the line(s) to retrieve.

        Returns:
            The line or list of lines requested.
        """


class Document(DocumentBase):
    """A document which can be opened in a TextArea."""

    def __init__(self, text: str) -> None:
        self._newline = _detect_newline_style(text)
        """The type of newline used in the text."""
        self._lines: list[str] = text.splitlines(keepends=False)
        """The lines of the document, excluding newline characters.

        If there's a newline at the end of the file, the final line is an empty string.
        """
        if text.endswith(tuple(VALID_NEWLINES)) or not text:
            self._lines.append("")

    @property
    def lines(self) -> list[str]:
        """Get the document as a list of strings, where each string represents a line.

        Newline characters are not included in at the end of the strings.

        The newline character used in this document can be found via the `Document.newline` property.
        """
        return self._lines

    @property
    def text(self) -> str:
        """Get the text from the document."""
        return self._newline.join(self._lines)

    @property
    def newline(self) -> Newline:
        """Get the Newline used in this document (e.g. '\r\n', '\n'. etc.)"""
        return self._newline

    def get_size(self, tab_width: int) -> Size:
        """The Size of the document, taking into account the tab rendering width.

        Args:
            tab_width: The width to use for tab indents.

        Returns:
            The size (width, height) of the document.
        """
        lines = self._lines
        cell_lengths = [cell_len(line.expandtabs(tab_width)) for line in lines]
        max_cell_length = max(cell_lengths, default=0)
        height = len(lines)
        return Size(max_cell_length, height)

    def replace_range(self, start: Location, end: Location, text: str) -> EditResult:
        """Replace text at the given range.

        This is the only method by which a document may be updated.

        Args:
            start: A tuple (row, column) where the edit starts.
            end: A tuple (row, column) where the edit ends.
            text: The text to insert between start and end.

        Returns:
            The EditResult containing information about the completed
                replace operation.
        """
        top, bottom = sorted((start, end))
        top_row, top_column = top
        bottom_row, bottom_column = bottom

        insert_lines = text.splitlines()
        if text.endswith(tuple(VALID_NEWLINES)):
            # Special case where a single newline character is inserted.
            insert_lines.append("")

        lines = self._lines

        replaced_text = self.get_text_range(top, bottom)
        if bottom_row >= len(lines):
            after_selection = ""
        else:
            after_selection = lines[bottom_row][bottom_column:]

        if top_row >= len(lines):
            before_selection = ""
        else:
            before_selection = lines[top_row][:top_column]

        if insert_lines:
            insert_lines[0] = before_selection + insert_lines[0]
            destination_column = len(insert_lines[-1])
            insert_lines[-1] = insert_lines[-1] + after_selection
        else:
            destination_column = len(before_selection)
            insert_lines = [before_selection + after_selection]

        lines[top_row : bottom_row + 1] = insert_lines
        destination_row = top_row + len(insert_lines) - 1

        end_location = (destination_row, destination_column)
        return EditResult(end_location, replaced_text)

    def get_text_range(self, start: Location, end: Location) -> str:
        """Get the text that falls between the start and end locations.

        Returns the text between `start` and `end`, including the appropriate
        line separator character as specified by `Document._newline`. Note that
        `_newline` is set automatically to the first line separator character
        found in the document.

        Args:
            start: The start location of the selection.
            end: The end location of the selection.

        Returns:
            The text between start (inclusive) and end (exclusive).
        """
        if start == end:
            return ""

        top, bottom = sorted((start, end))
        top_row, top_column = top
        bottom_row, bottom_column = bottom
        lines = self._lines
        if top_row == bottom_row:
            line = lines[top_row]
            selected_text = line[top_column:bottom_column]
        else:
            start_line = lines[top_row]
            end_line = lines[bottom_row] if bottom_row <= self.line_count - 1 else ""
            selected_text = start_line[top_column:]
            for row in range(top_row + 1, bottom_row):
                selected_text += self._newline + lines[row]

            if bottom_row < self.line_count:
                selected_text += self._newline
                selected_text += end_line[:bottom_column]

        return selected_text

    @property
    def line_count(self) -> int:
        """Returns the number of lines in the document."""
        return len(self._lines)

    @property
    def start(self) -> Location:
        """Returns the location of the start of the document (0, 0)."""
        return super().start

    @property
    def end(self) -> Location:
        """Returns the location of the end of the document."""
        last_line = self._lines[-1]
        return (self.line_count - 1, len(last_line))

    def get_index_from_location(self, location: Location) -> int:
        """Given a location, returns the index from the document's text.

        Args:
            location: The location in the document.

        Returns:
            The index in the document's text.
        """
        row, column = location
        index = row * len(self.newline) + column
        for line_index in range(row):
            index += len(self.get_line(line_index))
        return index

    def get_location_from_index(self, index: int) -> Location:
        """Given an index in the document's text, returns the corresponding location.

        Args:
            index: The index in the document's text.

        Returns:
            The corresponding location.
        """
        column_index = 0
        newline_length = len(self.newline)
        for line_index in range(self.line_count):
            next_column_index = (
                column_index + len(self.get_line(line_index)) + newline_length
            )
            if index < next_column_index:
                return (line_index, index - column_index)
            elif index == next_column_index:
                return (line_index + 1, 0)
            column_index = next_column_index

    def get_line(self, index: int) -> str:
        """Returns the line with the given index from the document.

        Args:
            index: The index of the line in the document.

        Returns:
            The string representing the line.
        """
        line_string = self[index]
        return line_string

    @overload
    def __getitem__(self, line_index: int) -> str: ...

    @overload
    def __getitem__(self, line_index: slice) -> list[str]: ...

    def __getitem__(self, line_index: int | slice) -> str | list[str]:
        """Return the content of a line as a string, excluding newline characters.

        Args:
            line_index: The index or slice of the line(s) to retrieve.

        Returns:
            The line or list of lines requested.
        """
        return self._lines[line_index]


Location = Tuple[int, int]
"""A location (row, column) within the document. Indexing starts at 0."""


class Selection(NamedTuple):
    """A range of characters within a document from a start point to the end point.
    The location of the cursor is always considered to be the `end` point of the selection.
    The selection is inclusive of the minimum point and exclusive of the maximum point.
    """

    start: Location = (0, 0)
    """The start location of the selection.

    If you were to click and drag a selection inside a text-editor, this is where you *started* dragging.
    """
    end: Location = (0, 0)
    """The end location of the selection.

    If you were to click and drag a selection inside a text-editor, this is where you *finished* dragging.
    """

    @classmethod
    def cursor(cls, location: Location) -> "Selection":
        """Create a Selection with the same start and end point - a "cursor".

        Args:
            location: The location to create the zero-width Selection.
        """
        return cls(location, location)

    @property
    def is_empty(self) -> bool:
        """Return True if the selection has 0 width, i.e. it's just a cursor."""
        start, end = self
        return start == end
