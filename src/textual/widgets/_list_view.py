from __future__ import annotations

from typing import ClassVar, Optional

from textual.await_remove import AwaitRemove
from textual.binding import Binding, BindingType
from textual.containers import Vertical
from textual.geometry import clamp
from textual.message import Message
from textual.reactive import reactive
from textual.widget import AwaitMount, Widget
from textual.widgets._list_item import ListItem


class ListView(Vertical, can_focus=True, can_focus_children=False):
    """A vertical list view widget.

    Displays a vertical list of `ListItem`s which can be highlighted and
    selected using the mouse or keyboard.

    Attributes:
        index: The index in the list that's currently highlighted.
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("enter", "select_cursor", "Select", show=False),
        Binding("up", "cursor_up", "Cursor Up", show=False),
        Binding("down", "cursor_down", "Cursor Down", show=False),
    ]
    """
    | Key(s) | Description |
    | :- | :- |
    | enter | Select the current item. |
    | up | Move the cursor up. |
    | down | Move the cursor down. |
    """

    index = reactive[Optional[int]](0, always_update=True)

    class Highlighted(Message, bubble=True):
        """Posted when the highlighted item changes.

        Highlighted item is controlled using up/down keys.
        Can be handled using `on_list_view_highlighted` in a subclass of `ListView`
        or in a parent widget in the DOM.

        Attributes:
            item: The highlighted item, if there is one highlighted.
        """

        def __init__(self, sender: ListView, item: ListItem | None) -> None:
            super().__init__(sender)
            self.item: ListItem | None = item

    class Selected(Message, bubble=True):
        """Posted when a list item is selected, e.g. when you press the enter key on it.

        Can be handled using `on_list_view_selected` in a subclass of `ListView` or in
        a parent widget in the DOM.

        Attributes:
            item: The selected item.
        """

        def __init__(self, sender: ListView, item: ListItem) -> None:
            super().__init__(sender)
            self.item: ListItem = item

    def __init__(
        self,
        *children: ListItem,
        initial_index: int | None = 0,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """
        Args:
            *children: The ListItems to display in the list.
            initial_index: The index that should be highlighted when the list is first mounted.
            name: The name of the widget.
            id: The unique ID of the widget used in CSS/query selection.
            classes: The CSS classes of the widget.
            disabled: Whether the ListView is disabled or not.
        """
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )
        self._index = initial_index

    def on_mount(self) -> None:
        """Ensure the ListView is fully-settled after mounting."""
        self.index = self._index

    @property
    def highlighted_child(self) -> ListItem | None:
        """The currently highlighted ListItem, or None if nothing is highlighted."""
        if self.index is not None and 0 <= self.index < len(self._nodes):
            list_item = self._nodes[self.index]
            assert isinstance(list_item, ListItem)
            return list_item
        else:
            return None

    def validate_index(self, index: int | None) -> int | None:
        """Clamp the index to the valid range, or set to None if there's nothing to highlight.

        Args:
            index: The index to clamp.

        Returns:
            The clamped index.
        """
        if not self._nodes or index is None:
            return None
        return self._clamp_index(index)

    def _clamp_index(self, index: int) -> int:
        """Clamp the index to a valid value given the current list of children"""
        last_index = max(len(self._nodes) - 1, 0)
        return clamp(index, 0, last_index)

    def _is_valid_index(self, index: int | None) -> bool:
        """Return True if the current index is valid given the current list of children"""
        if index is None:
            return False
        return 0 <= index < len(self._nodes)

    def watch_index(self, old_index: int, new_index: int) -> None:
        """Updates the highlighting when the index changes."""
        if self._is_valid_index(old_index):
            old_child = self._nodes[old_index]
            assert isinstance(old_child, ListItem)
            old_child.highlighted = False

        new_child: Widget | None
        if self._is_valid_index(new_index):
            new_child = self._nodes[new_index]
            assert isinstance(new_child, ListItem)
            new_child.highlighted = True
        else:
            new_child = None

        self._scroll_highlighted_region()
        self.post_message_no_wait(self.Highlighted(self, new_child))

    def append(self, item: ListItem) -> AwaitMount:
        """Append a new ListItem to the end of the ListView.

        Args:
            item: The ListItem to append.

        Returns:
            An awaitable that yields control to the event loop
                until the DOM has been updated with the new child item.
        """
        await_mount = self.mount(item)
        if len(self) == 1:
            self.index = 0
        return await_mount

    def clear(self) -> AwaitRemove:
        """Clear all items from the ListView.

        Returns:
            An awaitable that yields control to the event loop until
                the DOM has been updated to reflect all children being removed.
        """
        await_remove = self.query("ListView > ListItem").remove()
        self.index = None
        return await_remove

    def action_select_cursor(self) -> None:
        """Select the current item in the list."""
        selected_child = self.highlighted_child
        if selected_child is None:
            return
        self.post_message_no_wait(self.Selected(self, selected_child))

    def action_cursor_down(self) -> None:
        """Highlight the next item in the list."""
        if self.index is None:
            self.index = 0
            return
        self.index += 1

    def action_cursor_up(self) -> None:
        """Highlight the previous item in the list."""
        if self.index is None:
            self.index = 0
            return
        self.index -= 1

    def on_list_item__child_clicked(self, event: ListItem._ChildClicked) -> None:
        self.focus()
        self.index = self._nodes.index(event.sender)
        self.post_message_no_wait(self.Selected(self, event.sender))

    def _scroll_highlighted_region(self) -> None:
        """Used to keep the highlighted index within vision"""
        if self.highlighted_child is not None:
            self.scroll_to_widget(self.highlighted_child, animate=False)

    def __len__(self):
        return len(self._nodes)
