from __future__ import annotations

from typing import Iterator, overload, TYPE_CHECKING

import rich.repr

if TYPE_CHECKING:
    from .widget import Widget


@rich.repr.auto(angular=True)
class NodeList:
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

    def _append(self, widget: Widget) -> None:
        if widget not in self._nodes_set:
            self._nodes.append(widget)
            self._nodes_set.add(widget)
            self._updates += 1

    def _clear(self) -> None:
        if self._nodes:
            self._nodes.clear()
            self._nodes_set.clear()
            self._updates += 1

    def __iter__(self) -> Iterator[Widget]:
        return iter(self._nodes)

    @overload
    def __getitem__(self, index: int) -> Widget:
        ...

    @overload
    def __getitem__(self, index: slice) -> list[Widget]:
        ...

    def __getitem__(self, index: int | slice) -> Widget | list[Widget]:
        return self._nodes[index]
