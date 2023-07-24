from __future__ import annotations

from rich.text import Text

from textual._cells import cell_len
from textual._types import SupportsIndex
from textual.geometry import Size

# TODO - probably need to move _fix_direction either to this file or a standalone file.
from textual.widgets._text_area import _fix_direction


class Document:
    def __init__(self) -> None:
        self._lines: list[str] = []

    @property
    def lines(self) -> list[str]:
        return self._lines

    def load_text(self, text: str) -> None:
        """Load text from a string into the document.

        Args:
            text: The text to load into the document
        """
        lines = text.splitlines(keepends=False)
        if text[-1] == "\n":
            lines.append("")

        self._lines = lines

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
        if text.endswith("\n"):
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
            end_line = lines[bottom_row]

            deleted_text = start_line[top_column:] + "\n"
            for row in range(top_row + 1, bottom_row):
                deleted_text += lines[row] + "\n"

            deleted_text += end_line[:bottom_column]
            if bottom_column == len(end_line):
                deleted_text += "\n"

            # Update the lines at the start and end of the range
            lines[top_row] = start_line[:top_column] + end_line[bottom_column:]

            # Delete the lines in between
            del lines[top_row + 1 : bottom_row + 1]

        return deleted_text

    @property
    def size(self) -> Size:
        """Returns the size (width, height) of the document."""
        lines = self._lines
        text_width = max(cell_len(line) for line in lines)
        height = len(lines)
        # We add one to the text width to leave a space for the cursor, since it
        # can rest at the end of a line where there isn't yet any character.
        # Similarly, the cursor can rest below the bottom line of text, where
        # a line doesn't currently exist.
        return Size(text_width, height)

    @property
    def line_count(self) -> int:
        """Returns the number of lines in the document"""
        return len(self._lines)

    def get_line(self, index: int) -> Text:
        """Returns the line with the given index from the document"""
        line_string = self[index]
        line_string = line_string.replace("\n", "").replace("\r", "")
        return Text(line_string, end="", tab_size=4)

    def __getitem__(self, item: SupportsIndex | slice) -> str:
        return self._lines[item]
