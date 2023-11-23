import re

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

    @property
    def is_start_of_document_line(self, cursor: Location) -> bool:
        """True if and only if the cursor is on the first line."""
        return cursor[0] == 0

    @property
    def cursor_at_last_line(self) -> bool:
        """True if and only if the cursor is on the last line."""
        return self.selection.end[0] == self.document.line_count - 1

    @property
    def cursor_at_start_of_line(self) -> bool:
        """True if and only if the cursor is at column 0."""
        return self.selection.end[1] == 0

    @property
    def cursor_at_end_of_line(self) -> bool:
        """True if and only if the cursor is at the end of a row."""
        cursor_row, cursor_column = self.selection.end
        row_length = len(self.document[cursor_row])
        cursor_at_end = cursor_column == row_length
        return cursor_at_end

    @property
    def cursor_at_start_of_text(self) -> bool:
        """True if and only if the cursor is at location (0, 0)"""
        return self.selection.end == (0, 0)

    @property
    def cursor_at_end_of_text(self) -> bool:
        """True if and only if the cursor is at the very end of the document."""
        return self.cursor_at_last_line and self.cursor_at_end_of_line

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
