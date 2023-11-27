import re
from bisect import bisect_left
from typing import Any, Sequence

from textual.document._document import Location
from textual.document._wrapped_document import WrappedDocument


class DocumentNavigator:
    """Cursor navigation in the TextArea is "wrapping-aware".

    Although the cursor location (the selection) is represented as a location
    in the raw document, when you actually *move* the cursor, it must take wrapping
    into account (otherwise things start to look really confusing to the user where
    wrapping is involved).

    Your cursor visually moves through the wrapped version of the document, rather
    than the raw document. So, for example, pressing down on the keyboard
    may move your cursor to a position further along the current line,
    rather than on to the next line in the raw document.

    The class manages this behaviour.

    Given a cursor location in the unwrapped document, and a cursor movement action,
    this class can inform us of the destination the cursor will move to considering
    the current wrapping width and document content.

    For this to work correctly, the wrapped_document and document must be synchronised.
    This means that if you make an edit to the document, you *must* then update the
    wrapped document, and *then* you may query the document navigator.
    """

    def __init__(self, wrapped_document: WrappedDocument) -> None:
        """Create a CursorNavigator.

        Args:
            wrapped_document: The WrappedDocument to be used when making navigation decisions.
        """
        self._wrapped_document = wrapped_document
        self._document = wrapped_document.document

        self._word_pattern = re.compile(r"(?<=\W)(?=\w)|(?<=\w)(?=\W)")
        """Compiled regular expression for what we consider to be a 'word'."""

    def is_start_of_document_line(self, location: Location) -> bool:
        """True when the location is at the start of the first document line.

        Args:
            location: The location to check.

        Returns:
             True if the location is at column index 0.
        """
        return location[1] == 0

    def is_start_of_wrapped_line(self, location: Location) -> bool:
        """True when the location is at the start of the first wrapped line.

        Args:
            location: The location to check.

        Returns:
             True if the location is at column index 0.
        """
        if self.is_start_of_document_line(location):
            return True

        row, column = location
        wrap_offsets = self._wrapped_document.get_offsets(row)
        return index(wrap_offsets, column) != -1

    def is_end_of_document_line(self, location: Location) -> bool:
        """True if the location is at the end of a line in the document."""
        row, column = location
        row_length = len(self._document[row])
        return column == row_length

    def is_end_of_wrapped_line(self, location: Location) -> bool:
        """True if the location is at the end of a wrapped line."""
        if self.is_end_of_document_line(location):
            return True

        row, column = location
        wrap_offsets = self._wrapped_document.get_offsets(row)
        return index(wrap_offsets, column - 1) != -1

    def is_first_document_line(self, location: Location) -> bool:
        return location[0] == 0

    def is_first_wrapped_line(self, location: Location) -> bool:
        # TODO: Check the less than/equal to thing.
        # Ensure that the column index of the location is less (or equal to?!?!) than
        # the first value in the wrap offsets.
        if not self.is_first_document_line(location):
            return False

        row, column = location
        wrap_offsets = self._wrapped_document.get_offsets(row)

        if not wrap_offsets:
            return True

        if column <= wrap_offsets[0]:
            return True
        return False

    def is_last_document_line(self, location: Location) -> bool:
        """True when the location is on the last line of the document."""
        return location[0] == self._document.line_count - 1

    def is_last_wrapped_line(self, location: Location) -> bool:
        if not self.is_last_document_line(location):
            return False

        row, column = location
        wrap_offsets = self._wrapped_document.get_offsets(row)

        if not wrap_offsets:
            return True

        if column > wrap_offsets[-1]:
            return True
        return False

    def is_start_of_document(self, location: Location) -> bool:
        """True if and only if the cursor is at location (0, 0)"""
        return location == (0, 0)

    def is_end_of_document(self, location: Location) -> bool:
        return self.is_last_document_line(location) and self.is_end_of_document_line(
            location
        )

    def left(self, cursor: Location) -> Location:
        if cursor == (0, 0):
            return 0, 0

        cursor_row, cursor_column = cursor
        length_of_row_above = len(self._document[cursor_row - 1])
        target_row = cursor_row if cursor_column != 0 else cursor_row - 1
        target_column = cursor_column - 1 if cursor_column != 0 else length_of_row_above
        return target_row, target_column

    def right(self, cursor: Location) -> Location:
        # if
        #     return cursor

        cursor_row, cursor_column = cursor
        target_row = cursor_row + 1 if self.cursor_at_end_of_line else cursor_row
        target_column = 0 if self.cursor_at_end_of_line else cursor_column + 1
        return target_row, target_column


def index(sequence: Sequence, value: Any) -> int:
    """Locate the leftmost item in the sequence equal to value via bisection.

    Args:
        sequence: The sequence to search in.
        value: The value to find.

    Returns:
        The index of the value, or -1 if the value is not found in the sequence.
    """
    insert_index = bisect_left(sequence, value)
    if insert_index != len(sequence) and sequence[insert_index] == value:
        return insert_index
    return -1
