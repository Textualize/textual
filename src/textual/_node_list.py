from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, Iterator, Sequence, overload

import rich.repr

if TYPE_CHECKING:
    from .widget import Widget


class DuplicateIds(Exception):
    pass


@rich.repr.auto(angular=True)
class NodeList(Sequence["Widget"]):
    """
    A container for widgets that forms one level of hierarchy.

    Although named a list, widgets may appear only once, making them more like a set.

    """

    def __init__(self) -> None:
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
            self._updates += 1

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
            self._updates += 1

    def _ensure_unique_id(self, widget_id: str) -> None:
        if widget_id in self._nodes_by_id:
            raise DuplicateIds(
                f"Tried to insert a widget with ID {widget_id!r}, but a widget {self._nodes_by_id[widget_id]!r} "
                "already exists with that ID in this list of children. "
                "The children of a widget must have unique IDs."
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
            self._updates += 1

    def _clear(self) -> None:
        """Clear the node list."""
        if self._nodes:
            self._nodes.clear()
            self._nodes_set.clear()
            self._nodes_by_id.clear()
            self._updates += 1

    def __iter__(self) -> Iterator[Widget]:
        return iter(self._nodes)

    def __reversed__(self) -> Iterator[Widget]:
        return reversed(self._nodes)

    @overload
    def __getitem__(self, index: int) -> Widget:
        ...

    @overload
    def __getitem__(self, index: slice) -> list[Widget]:
        ...

    def __getitem__(self, index: int | slice) -> Widget | list[Widget]:
        return self._nodes[index]
