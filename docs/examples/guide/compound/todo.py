from __future__ import annotations

from todo_item import TodoItem

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer


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
        new_todo.set_status_message("Add description and due date.")

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


app = TODOApp()


if __name__ == "__main__":
    app.run()
