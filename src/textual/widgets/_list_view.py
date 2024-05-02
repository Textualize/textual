from __future__ import annotations

from typing import ClassVar, Iterable, Optional

from typing_extensions import TypeGuard

from .. import _widget_navigation
from ..await_remove import AwaitRemove
from ..binding import Binding, BindingType
from ..containers import VerticalScroll
from ..events import Mount
from ..message import Message
from ..reactive import reactive
from ..widget import AwaitMount
from ..widgets._list_item import ListItem


class ListView(VerticalScroll, can_focus=True, can_focus_children=False):
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

    index = reactive[Optional[int]](0, always_update=True, init=False)
    """The index of the currently highlighted item."""

    class Highlighted(Message):
        """Posted when the highlighted item changes.

        Highlighted item is controlled using up/down keys.
        Can be handled using `on_list_view_highlighted` in a subclass of `ListView`
        or in a parent widget in the DOM.
        """

        ALLOW_SELECTOR_MATCH = {"item"}
        """Additional message attributes that can be used with the [`on` decorator][textual.on]."""

        def __init__(self, list_view: ListView, item: ListItem | None) -> None:
            super().__init__()
            self.list_view: ListView = list_view
            """The view that contains the item highlighted."""
            self.item: ListItem | None = item
            """The highlighted item, if there is one highlighted."""

        @property
        def control(self) -> ListView:
            """The view that contains the item highlighted.

            This is an alias for [`Highlighted.list_view`][textual.widgets.ListView.Highlighted.list_view]
            and is used by the [`on`][textual.on] decorator.
            """
            return self.list_view

    class Selected(Message):
        """Posted when a list item is selected, e.g. when you press the enter key on it.

        Can be handled using `on_list_view_selected` in a subclass of `ListView` or in
        a parent widget in the DOM.
        """

        ALLOW_SELECTOR_MATCH = {"item"}
        """Additional message attributes that can be used with the [`on` decorator][textual.on]."""

        def __init__(self, list_view: ListView, item: ListItem) -> None:
            super().__init__()
            self.list_view: ListView = list_view
            """The view that contains the item selected."""
            self.item: ListItem = item
            """The selected item."""

        @property
        def control(self) -> ListView:
            """The view that contains the item selected.

            This is an alias for [`Selected.list_view`][textual.widgets.ListView.Selected.list_view]
            and is used by the [`on`][textual.on] decorator.
            """
            return self.list_view

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
        Initialize a ListView.

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
        # Set the index to the given initial index, or the first available index after.
        self._index = _widget_navigation.find_next_enabled(
            children,
            anchor=initial_index if initial_index is not None else None,
            direction=1,
            with_anchor=True,
        )

    def _on_mount(self, _: Mount) -> None:
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
        if index is None or not self._nodes:
            return None
        elif index < 0:
            return 0
        elif index >= len(self._nodes):
            return len(self._nodes) - 1

        return index

    def _is_valid_index(self, index: int | None) -> TypeGuard[int]:
        """Determine whether the current index is valid into the list of children."""
        if index is None:
            return False
        return 0 <= index < len(self._nodes)

    def watch_index(self, old_index: int | None, new_index: int | None) -> None:
        """Updates the highlighting when the index changes."""
        if self._is_valid_index(old_index):
            old_child = self._nodes[old_index]
            assert isinstance(old_child, ListItem)
            old_child.highlighted = False

        if self._is_valid_index(new_index) and not self._nodes[new_index].disabled:
            new_child = self._nodes[new_index]
            assert isinstance(new_child, ListItem)
            new_child.highlighted = True
            self._scroll_highlighted_region()
            self.post_message(self.Highlighted(self, new_child))
        else:
            self.post_message(self.Highlighted(self, None))

    def extend(self, items: Iterable[ListItem]) -> AwaitMount:
        """Append multiple new ListItems to the end of the ListView.

        Args:
            items: The ListItems to append.

        Returns:
            An awaitable that yields control to the event loop
                until the DOM has been updated with the new child items.
        """
        await_mount = self.mount(*items)
        if len(self) == 1:
            self.index = 0
        return await_mount

    def append(self, item: ListItem) -> AwaitMount:
        """Append a new ListItem to the end of the ListView.

        Args:
            item: The ListItem to append.

        Returns:
            An awaitable that yields control to the event loop
                until the DOM has been updated with the new child item.
        """
        return self.extend([item])

    def clear(self) -> AwaitRemove:
        """Clear all items from the ListView.

        Returns:
            An awaitable that yields control to the event loop until
                the DOM has been updated to reflect all children being removed.
        """
        await_remove = self.query("ListView > ListItem").remove()
        self.index = None
        return await_remove

    def insert(self, index: int, items: Iterable[ListItem]) -> AwaitMount:
        """Insert new ListItem(s) to specified index.

        Args:
            index: index to insert new ListItem.
            items: The ListItems to insert.

        Returns:
            An awaitable that yields control to the event loop
                until the DOM has been updated with the new child item.
        """
        await_mount = self.mount(*items, before=index)
        return await_mount

    def pop(self, index: Optional[int] = None) -> AwaitRemove:
        """Remove last ListItem from ListView or
           Remove ListItem from ListView by index

        Args:
            index: index of ListItem to remove from ListView

        Returns:
            An awaitable that yields control to the event loop until
                the DOM has been updated to reflect item being removed.
        """
        if index is None:
            await_remove = self.query("ListItem").last().remove()
        else:
            await_remove = self.query("ListItem")[index].remove()
        return await_remove

    def remove_items(self, indices: Iterable[int]) -> AwaitRemove:
        """Remove ListItems from ListView by indices

        Args:
            indices: index(s) of ListItems to remove from ListView

        Returns:
            An awaitable object that waits for the direct children to be removed.
        """
        items = self.query("ListItem")
        items_to_remove = []
        for index in indices:
            items_to_remove.append(items[index])

        await_remove = self.app._remove_nodes(items_to_remove, self)
        return await_remove

    def action_select_cursor(self) -> None:
        """Select the current item in the list."""
        selected_child = self.highlighted_child
        if selected_child is None:
            return
        self.post_message(self.Selected(self, selected_child))

    def action_cursor_down(self) -> None:
        """Highlight the next item in the list."""
        candidate = _widget_navigation.find_next_enabled(
            self._nodes,
            anchor=self.index,
            direction=1,
        )
        if self.index is not None and candidate is not None and candidate < self.index:
            return  # Avoid wrapping around.

        self.index = candidate

    def action_cursor_up(self) -> None:
        """Highlight the previous item in the list."""
        candidate = _widget_navigation.find_next_enabled(
            self._nodes,
            anchor=self.index,
            direction=-1,
        )
        if self.index is not None and candidate is not None and candidate > self.index:
            return  # Avoid wrapping around.

        self.index = candidate

    def _on_list_item__child_clicked(self, event: ListItem._ChildClicked) -> None:
        event.stop()
        self.focus()
        self.index = self._nodes.index(event.item)
        self.post_message(self.Selected(self, event.item))

    def _scroll_highlighted_region(self) -> None:
        """Used to keep the highlighted index within vision"""
        if self.highlighted_child is not None:
            self.call_after_refresh(
                self.scroll_to_widget, self.highlighted_child, animate=False
            )

    def __len__(self) -> int:
        """Compute the length (in number of items) of the list view."""
        return len(self._nodes)
