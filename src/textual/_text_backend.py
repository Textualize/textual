from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TextEditorBackend:
    """Represents a text editor (some text and a cursor)"""

    content: str = ""
    cursor_index: int = 0

    def set_content(self, text: str) -> None:
        """Set the content of the editor

        Args:
            text (str): The text to set as the content
        """
        self.content = text

    def delete_back(self) -> bool:
        """Delete the character behind the cursor and moves cursor back. If the
        cursor is at the start of the content, does nothing other than immediately
        return False.

        Returns:
            bool: True if the text content was modified. False otherwise.
        """
        if self.cursor_index == 0:
            return False

        new_text = (
            self.content[: self.cursor_index - 1] + self.content[self.cursor_index :]
        )
        self.content = new_text
        self.cursor_index = max(0, self.cursor_index - 1)
        return True

    def delete_forward(self) -> bool:
        """Delete the character in front of the cursor without moving the cursor.

        Returns:
            bool: True if the text content was modified. False otherwise.
        """
        if self.cursor_index == len(self.content):
            return False

        new_text = (
            self.content[: self.cursor_index] + self.content[self.cursor_index + 1 :]
        )
        self.content = new_text
        return True

    def cursor_left(self) -> bool:
        """Move the cursor 1 character left in the text. Is a noop if cursor is at start.

        Returns:
            bool: True if the cursor moved. False otherwise.
        """
        previous_index = self.cursor_index
        new_index = max(0, previous_index - 1)
        self.cursor_index = new_index
        return previous_index != new_index

    def cursor_right(self) -> bool:
        """Move the cursor 1 character right in the text. Is a noop if the cursor is at end.

        Returns:
            bool: True if the cursor moved. False otherwise.
        """
        previous_index = self.cursor_index
        new_index = min(len(self.content), previous_index + 1)
        self.cursor_index = new_index
        return previous_index != new_index

    def query_cursor_left(self) -> bool:
        """Check if the cursor can move 1 codepoint left in the text.

        Returns:
            bool: True if the cursor can move left. False otherwise.
        """
        previous_index = self.cursor_index
        new_index = max(0, previous_index - 1)
        return previous_index != new_index

    def query_cursor_right(self) -> str | None:
        """Check if the cursor can move right (we can't move right if we're at the end)
        and return the codepoint to the right of the cursor if it exists. If it doesn't
        exist (e.g. we're at the end), then return None

        Returns:
            str: The codepoint to the right of the cursor if it exists, otherwise None.
        """
        previous_index = self.cursor_index
        new_index = min(len(self.content), previous_index + 1)
        if new_index == len(self.content):
            return None
        elif previous_index != new_index:
            return self.content[new_index]
        return None

    def cursor_text_start(self) -> bool:
        """Move the cursor to the start of the text

        Returns:
            bool: True if the cursor moved. False otherwise.
        """
        if self.cursor_index == 0:
            return False

        self.cursor_index = 0
        return True

    def cursor_text_end(self) -> bool:
        """Move the cursor to the end of the text

        Returns:
            bool: True if the cursor moved. False otherwise.
        """
        text_length = len(self.content)
        if self.cursor_index == text_length:
            return False

        self.cursor_index = text_length
        return True

    def insert(self, text: str) -> bool:
        """Insert some text at the cursor position, and move the cursor
        to the end of the newly inserted text.

        Args:
            text: The text to insert

        Returns:
            bool: Always returns True since text should be insertable regardless of cursor location
        """
        new_text = (
            self.content[: self.cursor_index] + text + self.content[self.cursor_index :]
        )
        self.content = new_text
        self.cursor_index = min(len(self.content), self.cursor_index + len(text))
        return True

    def get_range(self, start: int, end: int) -> str:
        """Return the text between 2 indices. Useful for previews/views into
        a subset of the content e.g. scrollable single-line input fields

        Args:
            start (int): The starting index to return text from (inclusive)
            end (int): The index to return text up to (exclusive)

        Returns:
            str: The sliced string between start and end.
        """
        return self.content[start:end]

    @property
    def cursor_at_end(self):
        return self.cursor_index == len(self.content)
