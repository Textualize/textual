from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Sequence, overload

import rich.repr

if TYPE_CHECKING:
    from .widget import Widget


@rich.repr.auto(angular=True)
class NodeList(Sequence):
    """
    A container for widgets that forms one level of hierarchy.

    Although named a list, widgets may appear only once, making them more like a set.

    """

    def __init__(self) -> None:
        # The nodes in the list
        self._nodes: list[Widget] = []
        self._nodes_set: set[Widget] = set()
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

    def __contains__(self, widget: Widget) -> bool:
        return widget in self._nodes

    def index(self, widget: Widget) -> int:
        """Return the index of the given widget.

        Args:
            widget (Widget): The widget to find in the node list.

        Returns:
            int: The index of the widget in the node list.

        Raises:
            ValueError: If the widget is not in the node list.
        """
        return self._nodes.index(widget)

    def _append(self, widget: Widget) -> None:
        """Append a Widget.

        Args:
            widget (Widget): A widget.
        """
        if widget not in self._nodes_set:
            self._nodes.append(widget)
            self._nodes_set.add(widget)
            self._updates += 1

    def _insert(self, index: int, widget: Widget) -> None:
        """Insert a Widget.

        Args:
            widget (Widget): A widget.
        """
        if widget not in self._nodes_set:
            self._nodes.insert(index, widget)
            self._nodes_set.add(widget)
            self._updates += 1

    def _remove(self, widget: Widget) -> None:
        """Remove a widget from the list.

        Removing a widget not in the list is a null-op.

        Args:
            widget (Widget): A Widget in the list.
        """
        if widget in self._nodes_set:
            del self._nodes[self._nodes.index(widget)]
            self._nodes_set.remove(widget)
            self._updates += 1

    def _clear(self) -> None:
        """Clear the node list."""
        if self._nodes:
            self._nodes.clear()
            self._nodes_set.clear()
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
