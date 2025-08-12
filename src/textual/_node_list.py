from __future__ import annotations

import sys
import weakref
from operator import attrgetter
from typing import TYPE_CHECKING, Any, Callable, Iterable, Iterator, Sequence, overload

import rich.repr

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

    from textual.dom import DOMNode
    from textual.widget import Widget


class DuplicateIds(Exception):
    """Raised when attempting to add a widget with an id that already exists."""


class ReadOnlyError(AttributeError):
    """Raise if you try to mutate the list."""


@rich.repr.auto(angular=True)
class NodeList(Sequence["Widget"]):
    """
    A container for widgets that forms one level of hierarchy.

    Although named a list, widgets may appear only once, making them more like a set.
    """

    def __init__(self, parent: DOMNode | None = None) -> None:
        """Initialize a node list.

        Args:
            parent: The parent node which holds a reference to this object, or `None` if
                there is no parent.
        """
        self._parent = None if parent is None else weakref.ref(parent)
        # The nodes in the list
        self._nodes: list[Widget] = []
        self._nodes_set: set[Widget] = set()

        # We cache widgets by their IDs too for a quick lookup
        # Note that only widgets with IDs are cached like this, so
        # this cache will likely hold fewer values than self._nodes.
        self._nodes_by_id: dict[str, Widget] = {}

        # Increments when list is updated (used for caching)
        self._updates = 0

    def __bool__(self) -> bool:
        return bool(self._nodes)

    def __length_hint__(self) -> int:
        return len(self._nodes)

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._nodes

    def __len__(self) -> int:
        return len(self._nodes)

    def __contains__(self, widget: object) -> bool:
        return widget in self._nodes

    def updated(self) -> None:
        """Mark the nodes as having been updated."""
        self._updates += 1
        node = None if self._parent is None else self._parent()
        if node is None:
            return
        while node is not None and (node := node._parent) is not None:
            node._nodes._updates += 1

    def _sort(
        self,
        *,
        key: Callable[[Widget], SupportsRichComparison] | None = None,
        reverse: bool = False,
    ):
        """Sort nodes.

        Args:
            key: A key function which accepts a widget, or `None` for no key function.
            reverse: Sort in descending order.
        """
        if key is None:
            self._nodes.sort(key=attrgetter("sort_order"), reverse=reverse)
        else:
            self._nodes.sort(key=key, reverse=reverse)

        self.updated()

    def index(self, widget: Any, start: int = 0, stop: int = sys.maxsize) -> int:
        """Return the index of the given widget.

        Args:
            widget: The widget to find in the node list.

        Returns:
            The index of the widget in the node list.

        Raises:
            ValueError: If the widget is not in the node list.
        """
        return self._nodes.index(widget, start, stop)

    def _get_by_id(self, widget_id: str) -> Widget | None:
        """Get the widget for the given widget_id, or None if there's no matches in this list"""
        return self._nodes_by_id.get(widget_id)

    def _append(self, widget: Widget) -> None:
        """Append a Widget.

        Args:
            widget: A widget.
        """
        if widget not in self._nodes_set:
            self._nodes.append(widget)
            self._nodes_set.add(widget)
            widget_id = widget.id
            if widget_id is not None:
                self._ensure_unique_id(widget_id)
                self._nodes_by_id[widget_id] = widget
            self.updated()

    def _insert(self, index: int, widget: Widget) -> None:
        """Insert a Widget.

        Args:
            widget: A widget.
        """
        if widget not in self._nodes_set:
            self._nodes.insert(index, widget)
            self._nodes_set.add(widget)
            widget_id = widget.id
            if widget_id is not None:
                self._ensure_unique_id(widget_id)
                self._nodes_by_id[widget_id] = widget
            self.updated()

    def _ensure_unique_id(self, widget_id: str) -> None:
        """Ensure a new widget ID would be unique.

        Args:
            widget_id: New widget ID.

        Raises:
            DuplicateIds: If the given ID is not unique.
        """
        if widget_id in self._nodes_by_id:
            raise DuplicateIds(
                f"Tried to insert a widget with ID {widget_id!r}, but a widget already exists with that ID ({self._nodes_by_id[widget_id]!r}); "
                "ensure all child widgets have a unique ID."
            )

    def _remove(self, widget: Widget) -> None:
        """Remove a widget from the list.

        Removing a widget not in the list is a null-op.

        Args:
            widget: A Widget in the list.
        """
        if widget in self._nodes_set:
            del self._nodes[self._nodes.index(widget)]
            self._nodes_set.remove(widget)
            widget_id = widget.id
            if widget_id in self._nodes_by_id:
                del self._nodes_by_id[widget_id]
            self.updated()

    def _clear(self) -> None:
        """Clear the node list."""
        if self._nodes:
            self._nodes.clear()
            self._nodes_set.clear()
            self._nodes_by_id.clear()
            self.updated()

    def __iter__(self) -> Iterator[Widget]:
        return iter(self._nodes)

    def __reversed__(self) -> Iterator[Widget]:
        return reversed(self._nodes)

    @property
    def displayed(self) -> Iterable[Widget]:
        """Just the nodes where `display==True`."""
        for node in self._nodes:
            if node.display:
                yield node

    @property
    def displayed_reverse(self) -> Iterable[Widget]:
        """Just the nodes where `display==True`, in reverse order."""
        for node in reversed(self._nodes):
            if node.display:
                yield node

    if TYPE_CHECKING:

        @overload
        def __getitem__(self, index: int) -> Widget: ...

        @overload
        def __getitem__(self, index: slice) -> list[Widget]: ...

    def __getitem__(self, index: int | slice) -> Widget | list[Widget]:
        return self._nodes[index]

    def __getattr__(self, key: str) -> object:
        if key in {"clear", "append", "pop", "insert", "remove", "extend"}:
            raise ReadOnlyError(
                "Widget.children is read-only: use Widget.mount(...) or Widget.remove(...) to add or remove widgets"
            )
        raise AttributeError(key)
