from __future__ import annotations

import datetime as dt

from date_picker import DatePicker
from editabletext import EditableText

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Button, Input, Label, Static, Switch


class TodoItem(Static):
    """Widget that represents a TODO item with a description and a due date."""

    DEFAULT_CSS = ...  # (1)!

    _show_more: Button
    """Sub widget to toggle the extra details about the TODO item."""
    _done: Switch
    """Sub widget to tick a TODO item as complete."""
    _description: EditableText
    """Sub widget holding the description of the TODO item."""
    _top_row: Horizontal
    """The top row of the widget."""
    _status: Label
    """Sub widget showing status information."""
    _due_date_label: Label
    """Sub widget labeling the date picker."""
    _date_picker: DatePicker
    """Sub widget to select due date."""
    _bot_row: Horizontal
    """The bottom row of the widget."""

    _cached_date: None | dt.date = None
    """The date in cache."""

    class DueDateChanged(Message):  # (2)!
        """Posted when the due date changes."""

        sender: TodoItem

        def __init__(self, sender: TodoItem, date: dt.date) -> None:
            super().__init__(sender)
            self.date = date

    class DueDateCleared(Message):  # (3)!
        """Posted when the due date is reset."""

        sender: TodoItem

    class Done(Message):  # (4)!
        """Posted when the TODO item is checked off."""

        sender: TodoItem

    def compose(self) -> ComposeResult:
        self._show_more = Button("v", classes="todoitem--show-more")
        self._done = Switch(classes="todoitem--done")
        self._description = EditableText(classes="todoitem--description")
        self._top_row = Horizontal(
            self._show_more,
            self._done,
            self._description,
            classes="todoitem--top-row",
        )

        self._due_date_label = Label("Due date:", classes="todoitem--duedate")
        self._date_picker = DatePicker(classes="todoitem--datepicker")
        self._status = Label("", classes="todoitem--status")
        self._bot_row = Horizontal(
            self._status,
            self._due_date_label,
            self._date_picker,
            classes="todoitem--bot-row",
        )

        yield self._top_row
        yield self._bot_row

    def on_mount(self) -> None:
        self._description.switch_to_editing_mode()  # (5)!
        self._date_picker.switch_to_editing_mode()
        self.query(Input).first().focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Toggle the collapsed state."""
        event.stop()
        self._show_more.label = ">" if str(self._show_more.label) == "v" else "v"
        self.toggle_class("todoitem--collapsed")

    def on_switch_changed(self, event: Switch.Changed) -> None:  # (6)!
        """Emit event saying the TODO item was completed."""
        event.stop()
        self.post_message_no_wait(self.Done(self))

    def on_date_picker_selected(self, event: DatePicker.Selected) -> None:  # (7)!
        """Colour the TODO item according to its deadline."""
        event.stop()
        date = event.date
        if date == self._cached_date:
            return

        self._cached_date = date
        self.set_status_message("Date updated.", 1)
        if date is None:
            self.post_message_no_wait(self.DueDateCleared(self))
            return

        today = dt.date.today()
        self.remove_class(
            "todoitem--due-late", "todoitem--due-today", "todoitem--due-in-time"
        )
        if date < today:
            self.add_class("todoitem--due-late")
        elif date == today:
            self.add_class("todoitem--due-today")
        else:
            self.add_class("todoitem--due-in-time")

        self.post_message_no_wait(self.DueDateChanged(self, date))

    def on_date_picker_cleared(self, event: DatePicker.Cleared) -> None:
        """Clear all styling from a TODO item with no due date."""

        event.stop()
        if self._cached_date is None:
            return

        self._cached_date = None
        self.set_status_message("Date cleared.", 1)
        self.remove_class(
            "todoitem--due-late",
            "todoitem--due-today",
            "todoitem--due-in-time",
        )

        self.post_message_no_wait(self.DueDateCleared(self))

    @property
    def date(self) -> dt.date | None:  # (8)!
        """Date the item is due by, or None if not set."""
        if self._cached_date is None:
            self._cached_date = self._date_picker.date
        return self._cached_date

    def reset_status(self) -> None:  # (9)!
        """Resets the status message to indicate time to deadline."""
        self._status.renderable = ""
        today = dt.date.today()
        date = self.date

        if date is None:
            self.set_status_message("")
            return

        delta = (date - today).days
        if delta > 1:
            self.set_status_message(f"Due in {delta} days.")
        elif delta == 1:
            self.set_status_message("Due in 1 day.")
        elif delta == 0:
            self.set_status_message("Due today.")
        elif delta == -1:
            self.set_status_message("1 day late!")
        else:
            self.set_status_message(f"{abs(delta)} days late!")

    def set_status_message(
        self, status: str, duration: float | None = None
    ) -> None:  # (10)!
        """Set the status for a determined period of time.

        Args:
            status: The new status message.
            duration: How many seconds to keep the status message for.
                Setting this to None will keep it there until it is changed again.
        """
        self._status.renderable = status
        self._status.refresh()

        if duration is not None:
            self.set_timer(duration, self.reset_status)
