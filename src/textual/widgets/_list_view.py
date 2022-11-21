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
        """Get the currently highlighted ListItem

        Returns:
            ListItem | None: The currently highlighted ListItem, or None if nothing is highlighted.
        """
        if self.index is None:
            return None
        elif 0 <= self.index < len(self.children):
            return self.children[self.index]

    def validate_index(self, index: int | None) -> int | None:
        if not self.children or index is None:
            return None
        return self._clamp_index(index)

    def _clamp_index(self, index: int) -> int:
        """Clamp the index to a valid value given the current list of children"""
        last_index = max(len(self.children) - 1, 0)
        return clamp(index, 0, last_index)

    def _is_valid_index(self, index: int | None) -> bool:
        """Return True if the current index is valid given the current list of children"""
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

    async def append(self, item: ListItem) -> None:
        """Append a new ListItem to the end of the ListView.

        Args:
            item (ListItem): The ListItem to append.
        """
        await self.mount(item)
        if len(self) == 1:
            self.index = 0
        await self.emit(self.ChildrenUpdated(self, self.children))

    async def clear(self) -> None:
        """Clear all items from the ListView."""
        await self.query("ListView > ListItem").remove()
        await self.emit(self.ChildrenUpdated(self, self.children))

    def action_select(self) -> None:
        selected_child = self.highlighted_child
        self.emit_no_wait(self.Selected(self, selected_child))

    def on_list_item__child_clicked(self, event: ListItem._ChildClicked) -> None:
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
        """Used to keep the highlighted index within vision"""
        if self.highlighted_child is not None:
            self.scroll_to_widget(self.highlighted_child, animate=False)

    def __len__(self):
        return len(self.children)

    class Highlighted(Message, bubble=True):
        """Emitted when the highlighted item changes. Highlighted item is controlled using up/down keys"""

        def __init__(self, sender: ListView, item: ListItem | None) -> None:
            super().__init__(sender)
            self.item = item

    class Selected(Message, bubble=True):
        """Emitted when a list item is selected, e.g. when you press the enter key on it"""

        def __init__(self, sender: ListView, item: ListItem) -> None:
            super().__init__(sender)
            self.item = item

    class ChildrenUpdated(Message, bubble=True):
        """Emitted when the elements in the `ListView` are changed (e.g. a child is
        added, or the list is cleared)"""

        def __init__(self, sender: ListView, children: list[ListItem]) -> None:
            super().__init__(sender)
            self.children = children
