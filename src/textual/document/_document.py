from __future__ import annotations

from typing import NamedTuple, Tuple

from rich.text import Text

from textual._fix_direction import _fix_direction
from textual._types import Literal, SupportsIndex, get_args

Newline = Literal["\r\n", "\n", "\r"]
VALID_NEWLINES = set(get_args(Newline))


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


class Document:
    def __init__(self, text: str) -> None:
        self._newline = _detect_newline_style(text)
        """The type of newline used in the text."""
        self._lines: list[str] = text.splitlines(keepends=False)
        """The lines of the document, excluding newline characters.

        If there's a newline at the end of the file, the final line is an empty string.
        """
        if text.endswith(tuple(VALID_NEWLINES)):
            self._lines.append("")

    @property
    def lines(self) -> list[str]:
        return self._lines

    @property
    def content(self) -> str:
        return self._newline.join(self._lines)

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

    def delete_range(self, start: tuple[int, int], end: tuple[int, int]) -> str:
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

        if top_row == bottom_row:
            # The deletion range is within a single line.
            line = lines[top_row]
            deleted_text = line[top_column:bottom_column]
            lines[top_row] = line[:top_column] + line[bottom_column:]
        else:
            # The deletion range spans multiple lines.
            start_line = lines[top_row]

            deleted_text = start_line[top_column:]
            for row in range(top_row + 1, bottom_row):
                deleted_text += self._newline + lines[row]

            # Now handle the bottom line of the selection
            end_line = lines[bottom_row] if bottom_row <= self.line_count - 1 else ""

            # Only include the newline if the endline actually exists
            if bottom_row < self.line_count:
                deleted_text += self._newline
                deleted_text += end_line[:bottom_column]

            # Update the lines at the start and end of the range
            lines[top_row] = start_line[:top_column] + end_line[bottom_column:]

            # Delete the lines in between
            del lines[top_row + 1 : bottom_row + 1]

        return deleted_text

    @property
    def line_count(self) -> int:
        """Returns the number of lines in the document"""
        return len(self._lines)

    def get_line_text(self, index: int) -> Text:
        """Returns the line with the given index from the document"""
        line_string = self[index]
        line_string = line_string.replace("\n", "").replace("\r", "")
        return Text(line_string, end="")

    def __getitem__(self, item: SupportsIndex | slice) -> str:
        return self._lines[item]


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
