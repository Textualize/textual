from __future__ import annotations

import datetime as dt

from editabletext import EditableText

from textual.app import ComposeResult
from textual.message import Message


class DatePicker(EditableText):
    class Cleared(Message):
        """Posted when the date selected is cleared."""

    class Selected(Message):
        """Posted when a valid date is selected."""

        def __init__(self, sender: DatePicker, date: dt.date) -> None:
            super().__init__(sender)
            self.date = date

    def compose(self) -> ComposeResult:
        super_compose = list(super().compose())
        self._input.placeholder = "dd-mm-yy"
        yield from super_compose

    def switch_to_display_mode(self) -> None:
        """Switch to display mode only if the date is empty or valid."""
        if self._input.value and self.date is None:
            self.app.bell()
            return
        return super().switch_to_display_mode()

    def on_editable_text_display(self, event: EditableText.Display) -> None:
        event.stop()
        date = self.date
        if date is None:
            self.post_message_no_wait(self.Cleared(self))
        else:
            self.post_message_no_wait(self.Selected(self, date))

    def on_editable_text_edit(self, event: EditableText.Edit) -> None:
        event.stop()

    @property
    def date(self) -> dt.date | None:
        """The date picked or None if not available."""
        try:
            return dt.datetime.strptime(self._input.value, "%d-%m-%Y").date()
        except ValueError:
            return None
