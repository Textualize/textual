from __future__ import annotations

from textual import events
from textual.await_remove import AwaitRemove
from textual.binding import Binding
from textual.containers import Vertical
from textual.geometry import clamp
from textual.message import Message
from textual.reactive import reactive
from textual.widget import AwaitMount
from textual.widgets._list_item import ListItem


class ListView(Vertical, can_focus=True, can_focus_children=False):
    """Displays a vertical list of `ListItem`s which can be highlighted
    and selected using the mouse or keyboard.

    Attributes:
        index: The index in the list that's currently highlighted.
    """

    DEFAULT_CSS = """
    ListView {
        scrollbar-size-vertical: 2;
    }
    """

    BINDINGS = [
        Binding("down", "cursor_down", "Down", show=False),
        Binding("up", "cursor_up", "Up", show=False),
        Binding("enter", "select_cursor", "Select", show=False),
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
        """
        Args:
            *children: The ListItems to display in the list.
            initial_index: The index that should be highlighted when the list is first mounted.
            name: The name of the widget.
            id: The unique ID of the widget used in CSS/query selection.
            classes: The CSS classes of the widget.
        """
        super().__init__(*children, name=name, id=id, classes=classes)
        self.index = initial_index

    @property
    def highlighted_child(self) -> ListItem | None:
        """ListItem | None: The currently highlighted ListItem,
        or None if nothing is highlighted.
        """
        if self.index is None:
            return None
        elif 0 <= self.index < len(self.children):
            return self.children[self.index]

    def validate_index(self, index: int | None) -> int | None:
        """Clamp the index to the valid range, or set to None if there's nothing to highlight."""
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
        """Updates the highlighting when the index changes."""
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

    def append(self, item: ListItem) -> AwaitMount:
        """Append a new ListItem to the end of the ListView.

        Args:
            item (ListItem): The ListItem to append.

        Returns:
            AwaitMount: An awaitable that yields control to the event loop
                until the DOM has been updated with the new child item.
        """
        await_mount = self.mount(item)
        if len(self) == 1:
            self.index = 0
        return await_mount

    def clear(self) -> AwaitRemove:
        """Clear all items from the ListView.

        Returns:
            AwaitRemove: An awaitable that yields control to the event loop until
                the DOM has been updated to reflect all children being removed.
        """
        await_remove = self.query("ListView > ListItem").remove()
        self.index = None
        return await_remove

    def action_select_cursor(self) -> None:
        selected_child = self.highlighted_child
        self.emit_no_wait(self.Selected(self, selected_child))

    def action_cursor_down(self) -> None:
        self.index += 1

    def action_cursor_up(self) -> None:
        self.index -= 1

    def on_list_item__child_clicked(self, event: ListItem._ChildClicked) -> None:
        self.focus()
        self.index = self.children.index(event.sender)
        self.emit_no_wait(self.Selected(self, event.sender))

    def _scroll_highlighted_region(self) -> None:
        """Used to keep the highlighted index within vision"""
        if self.highlighted_child is not None:
            self.scroll_to_widget(self.highlighted_child, animate=False)

    def __len__(self):
        return len(self.children)

    class Highlighted(Message, bubble=True):
        """Emitted when the highlighted item changes. Highlighted item is controlled using up/down keys.

        Attributes:
            item (ListItem | None): The highlighted item, if there is one highlighted.
        """

        def __init__(self, sender: ListView, item: ListItem | None) -> None:
            super().__init__(sender)
            self.item = item

    class Selected(Message, bubble=True):
        """Emitted when a list item is selected, e.g. when you press the enter key on it

        Attributes:
            item (ListItem): The selected item.
        """

        def __init__(self, sender: ListView, item: ListItem) -> None:
            super().__init__(sender)
            self.item = item
