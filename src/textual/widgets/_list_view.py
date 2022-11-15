from __future__ import annotations

import asyncio
from asyncio import Future

from textual import events
from textual.binding import Binding
from textual.containers import Vertical
from textual.geometry import clamp
from textual.message import Message
from textual.reactive import reactive
from textual.widgets._list_item import ListItem


class ListView(Vertical, can_focus=True, can_focus_children=False):
    DEFAULT_CSS = """
    ListView {
        scrollbar-size-vertical: 1;
    }
    """

    BINDINGS = [
        Binding("down", "down", "Down"),
        Binding("up", "up", "Up"),
        Binding("enter", "select", "Select"),
    ]

    index = reactive(0, always_update=True)

    def __init__(
        self,
        *children: ListItem,
        initial_index: int | None = 0,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes)
        self.index = initial_index

    @property
    def highlighted_child(self) -> ListItem | None:
        if 0 <= self.index < len(self.children):
            return self.children[self.index]
        return None

    def validate_index(self, index: int | None) -> int | None:
        if not self.children:
            return None
        return self._clamp_index(index)

    def _clamp_index(self, index: int) -> int:
        last_index = max(len(self.children) - 1, 0)
        return clamp(index, 0, last_index)

    def _is_valid_index(self, index: int | None) -> bool:
        if index is None:
            return False
        return 0 <= index < len(self.children)

    def watch_index(self, old_index: int, new_index: int) -> None:
        if self._is_valid_index(old_index):
            old_child = self.children[old_index]
            old_child.highlighted = False
        if self._is_valid_index(new_index):
            new_child = self.children[new_index]
            new_child.highlighted = True
        else:
            new_child = None

        self._scroll_highlighted_region()
        self.emit_no_wait(self.Highlighted(self, new_child))

    def append(self, item: ListItem) -> None:
        """Append a new ListItem to the end of the ListView.

        Args:
            item (ListItem): The ListItem to append.
        """
        self._add_child(item)
        if len(self) > 0:
            self.index = 1

    def clear(self) -> Future:
        """Clear all items from the ListView."""
        self.index = None
        await_removes = []
        for child in reversed(self.children):
            await_removes.append(child.remove())
        return asyncio.gather(*await_removes)

    def action_select(self) -> None:
        selected_child = self.highlighted_child
        self.emit_no_wait(self.Selected(self, selected_child))

    def on_list_item_child_selected(self, event: ListItem.ChildSelected) -> None:
        self.focus()
        self.index = self.children.index(event.sender)
        self.emit_no_wait(self.Selected(self, event.sender))

    def key_up(self, event: events.Key) -> None:
        event.stop()
        event.prevent_default()
        self.index -= 1

    def key_down(self, event: events.Key) -> None:
        event.stop()
        event.prevent_default()
        self.index += 1

    def _scroll_highlighted_region(self) -> None:
        if self.highlighted_child is not None:
            self.scroll_to_widget(self.highlighted_child, animate=False)

    def __len__(self):
        return len(self.children)

    class Highlighted(Message, bubble=True):
        def __init__(self, sender: ListView, item: ListItem | None) -> None:
            super().__init__(sender)
            self.item = item

    class Selected(Message, bubble=True):
        def __init__(self, sender: ListView, item: ListItem) -> None:
            super().__init__(sender)
            self.item = item
