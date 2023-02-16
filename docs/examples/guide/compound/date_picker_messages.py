from __future__ import annotations

import datetime as dt

from editabletext import EditableText

from textual.app import ComposeResult
from textual.message import Message


class DatePicker(EditableText):
    class DateCleared(Message):  # (1)!
        """Posted when the date selected is cleared."""

    class Selected(Message):  # (2)!
        """Posted when a valid date is selected."""

        def __init__(self, sender: DatePicker, date: dt.date) -> None:
            super().__init__(sender)
            self.date = date

    def on_editable_text_display(self, event: EditableText.Display) -> None:  # (3)!
        event.stop()
        date = self.date
        if date is None:
            self.post_message_no_wait(self.DateCleared(self))
        else:
            self.post_message_no_wait(self.Selected(self, date))

    def on_editable_text_edit(self, event: EditableText.Edit) -> None:  # (4)!
        event.stop()
