from __future__ import annotations

from abc import ABC, abstractmethod
from functools import lru_cache
from typing import NamedTuple, Tuple

from rich.text import Text

from textual._cells import cell_len
from textual._fix_direction import _fix_direction
from textual._types import Literal, SupportsIndex, get_args
from textual.geometry import Size

Newline = Literal["\r\n", "\n", "\r"]
"""The type representing valid line separators."""
VALID_NEWLINES = set(get_args(Newline))
"""The set of valid line separator strings."""


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
        The NewlineStyle used in the file.
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
    def insert_range(self, start: Location, end: Location, text: str) -> Location:
        """Insert text at the given range.

        Args:
            start: A tuple (row, column) where the edit starts.
            end: A tuple (row, column) where the edit ends.
            text: The text to insert between start and end.

        Returns:
            The new end location after the edit is complete.
        """

    @abstractmethod
    def delete_range(self, start: Location, end: Location) -> str:
        """Delete the text at the given range.

        Args:
            start: A tuple (row, column) where the edit starts.
            end: A tuple (row, column) where the edit ends.

        Returns:
            The text that was deleted from the document.
        """

    @property
    @abstractmethod
    def text(self) -> str:
        """The text from the document as a string."""

    @abstractmethod
    def get_line_text(self, index: int) -> Text:
        """Returns the line with the given index from the document.

        This is used in rendering lines, and will be called by the
        TextArea for each line that is rendered.

        Args:
            index: The index of the line in the document.

        Returns:
            The Text instance representing the line. When overriding
            this method, ensure the returned Text instance has `end=""`.
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

        The height will generally be the number of lines, and the width
        will be the maximum cell length of all the lines."""

    @property
    @abstractmethod
    def line_count(self) -> int:
        """Returns the number of lines in the document."""


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
        max_cell_length = max(cell_lengths or [0])
        height = len(lines)
        return Size(max_cell_length, height)

    def insert_range(self, start: Location, end: Location, text: str) -> Location:
        """Insert text at the given range.

        Args:
            start: A tuple (row, column) where the edit starts.
            end: A tuple (row, column) where the edit ends.
            text: The text to insert between start and end.

        Returns:
            The new end location after the edit is complete.
        """
        if not text:
            return end

        top, bottom = _fix_direction(start, end)
        top_row, top_column = top
        bottom_row, bottom_column = bottom

        insert_lines = text.splitlines()
        if text.endswith(tuple(VALID_NEWLINES)):
            # Special case where a single newline character is inserted.
            insert_lines.append("")

        lines = self._lines

        before_selection = lines[top_row][:top_column]
        after_selection = lines[bottom_row][bottom_column:]

        insert_lines[0] = before_selection + insert_lines[0]
        destination_column = len(insert_lines[-1])
        insert_lines[-1] = insert_lines[-1] + after_selection

        lines[top_row : bottom_row + 1] = insert_lines
        destination_row = top_row + len(insert_lines) - 1

        end_point = destination_row, destination_column
        return end_point

    def delete_range(self, start: Location, end: Location) -> str:
        """Delete the text at the given range.

        Args:
            start: A tuple (row, column) where the edit starts.
            end: A tuple (row, column) where the edit ends.

        Returns:
            The text that was deleted from the document.
        """
        top, bottom = _fix_direction(start, end)
        top_row, top_column = top
        bottom_row, bottom_column = bottom

        lines = self._lines

        deleted_text = self.get_text_range(top, bottom)

        if top_row == bottom_row:
            line = lines[top_row]
            lines[top_row] = line[:top_column] + line[bottom_column:]
        else:
            start_line = lines[top_row]
            end_line = lines[bottom_row] if bottom_row <= self.line_count - 1 else ""
            lines[top_row] = start_line[:top_column] + end_line[bottom_column:]
            del lines[top_row + 1 : bottom_row + 1]

        return deleted_text

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
        top, bottom = _fix_direction(start, end)
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

    def get_line_text(self, index: int) -> Text:
        """Returns the line with the given index from the document.

        Args:
            index: The index of the line in the document.

        Returns:
            The Text instance representing the line. When overriding
            this method, ensure the returned Text instance has `end=""`.
        """
        line_string = self[index]
        line_string = line_string.replace("\n", "").replace("\r", "")
        return Text(line_string, end="")

    def __getitem__(self, line_index: SupportsIndex | slice) -> str | list[str]:
        """Return the content of a line as a string, excluding newline characters.

        Args:
            line_index: The index or slice of the line(s) to retrieve.

        Returns:
            The line or list of lines requested.
        """
        return self._lines[line_index]


Location = Tuple[int, int]
"""A location (row, column) within the document."""


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

    @property
    def range(self) -> tuple[Location, Location]:
        """Return the Selection as a "standard" range, from top to bottom i.e. (minimum point, maximum point)
        where the minimum point is inclusive and the maximum point is exclusive."""
        start, end = self
        return _fix_direction(start, end)
