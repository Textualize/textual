from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TextEditorBackend:
    content: str = ""
    cursor_index: int = 0

    def set_content(self, text: str):
        self.content = text

    def delete_back(self) -> bool:
        """Delete the character behind the cursor

        Returns: True if the text content was modified. False otherwise.
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
        """Delete the character in front of the cursor

        Returns: True if the text content was modified. False otherwise.
        """
        if self.cursor_index == len(self.content):
            return False

        new_text = (
            self.content[: self.cursor_index] + self.content[self.cursor_index + 1 :]
        )
        self.content = new_text
        return True

    def cursor_left(self) -> bool:
        """Move the cursor 1 character left in the text"""
        previous_index = self.cursor_index
        new_index = max(0, previous_index - 1)
        self.cursor_index = new_index
        return previous_index != new_index

    def cursor_right(self) -> bool:
        """Move the cursor 1 character right in the text"""
        previous_index = self.cursor_index
        new_index = min(len(self.content), previous_index + 1)
        self.cursor_index = new_index
        return previous_index != new_index

    def query_cursor_left(self) -> bool:
        """Check if the cursor can move 1 character left in the text"""
        previous_index = self.cursor_index
        new_index = max(0, previous_index - 1)
        return previous_index != new_index

    def query_cursor_right(self) -> bool:
        """Check if the cursor can move right"""
        previous_index = self.cursor_index
        new_index = min(len(self.content), previous_index + 1)
        return previous_index != new_index

    def cursor_text_start(self) -> bool:
        if self.cursor_index == 0:
            return False

        self.cursor_index = 0
        return True

    def cursor_text_end(self) -> bool:
        text_length = len(self.content)
        if self.cursor_index == text_length:
            return False

        self.cursor_index = text_length
        return True

    def insert_at_cursor(self, text: str) -> bool:
        new_text = (
            self.content[: self.cursor_index] + text + self.content[self.cursor_index :]
        )
        self.content = new_text
        self.cursor_index = min(len(self.content), self.cursor_index + len(text))
        return True

    def get_range(self, start: int, end: int) -> str:
        """Return the text between 2 indices. Useful for previews/views into
        a subset of the content e.g. scrollable single-line input fields"""
        return self.content[start:end]
