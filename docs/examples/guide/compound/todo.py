from __future__ import annotations

import datetime as dt

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import Button, Checkbox, Footer, Label, Static

from editabletext05 import EditableText


class DatePicker(EditableText):
    class DateCleared(Message):
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
            self.post_message_no_wait(self.DateCleared(self))
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


class TodoItem(Static):
    """Widget that represents a TODO item with a description and a due date."""

    _show_more: Button
    """Sub widget to toggle the extra details about the TODO item."""
    _done: Checkbox
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

    class DueDateChanged(Message):
        """Posted when the due date changes."""

        sender: TodoItem

        def __init__(self, sender: TodoItem, date: dt.date) -> None:
            super().__init__(sender)
            self.date = date

    class Done(Message):
        """Posted when the TODO item is checked off."""

        sender: TodoItem

    def compose(self) -> ComposeResult:
        self._show_more = Button("v", classes="todoitem--show-more")
        self._done = Checkbox(classes="todoitem--done")
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
        self._date_picker.switch_to_editing_mode()

    def on_button_pressed(self) -> None:
        """Toggle the collapsed state."""
        self._show_more.label = ">" if str(self._show_more.label) == "v" else "v"
        self.toggle_class("todoitem--collapsed")

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Emit event saying the TODO item was completed."""
        event.stop()
        self.post_message_no_wait(self.Done(self))

    @property
    def date(self) -> dt.date | None:
        """Date the item is due by, or None if not set."""
        if self._cached_date is None:
            self._cached_date = self._date_picker.date
        return self._cached_date

    def reset_status(self) -> None:
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

    def set_status_message(self, status: str, duration: float | None = None) -> None:
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

    def on_date_picker_selected(self, event: DatePicker.Selected) -> None:
        """Colour the TODO item according to its deadline."""
        date = event.date
        if date == self._cached_date:
            return

        self._cached_date = date
        self.set_status_message("Date updated.", 1)
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


class TODOApp(App[None]):
    BINDINGS = [
        ("n", "new_todo", "New"),
    ]

    _todo_container: Vertical
    """Container for all the TODO items that are due."""

    def compose(self) -> ComposeResult:
        self._todo_container = Vertical(id="todo-container")
        yield self._todo_container
        yield Footer()

    async def action_new_todo(self) -> None:
        """Add a new TODO item to the list."""
        new_todo = TodoItem()
        await self._todo_container.mount(new_todo)
        new_todo.scroll_visible()

    def on_todo_item_due_date_changed(self, event: TodoItem.DueDateChanged) -> None:
        self._sort_todo_item(event.sender)

    async def on_todo_item_done(self, event: TodoItem.Done) -> None:
        await event.sender.remove()

    def _sort_todo_item(self, item: TodoItem) -> None:
        """Sort the given TODO item in order, by date."""

        if len(self._todo_container.children) == 1:
            return

        date = item.date
        # If the date is None, move the TODO item to the end.
        if date is None:
            self._todo_container.move_child(
                item, len(self._todo_container.children) - 1
            )
            return

        for idx, todo in enumerate(self._todo_container.query(TodoItem)):
            if todo.date is None or todo.date > date:
                self._todo_container.move_child(item, idx)
                return

        end = len(self._todo_container.children) - 1
        if self._todo_container.children[end] != item:
            self._todo_container.move_child(item, after=end)


app = TODOApp(css_path="todo.css")


if __name__ == "__main__":
    app.run()
