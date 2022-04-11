from __future__ import annotations

from typing import Iterator, overload, TYPE_CHECKING
from weakref import ref

import rich.repr

if TYPE_CHECKING:
    from .dom import DOMNode


@rich.repr.auto
class NodeList:
    """
    A container for widgets that forms one level of hierarchy.

    Although named a list, widgets may appear only once, making them more like a set.

    """

    def __init__(self) -> None:
        self._nodes: list[DOMNode] = []

    def __bool__(self) -> bool:
        return bool(self._nodes)

    def __length_hint__(self) -> int:
        return len(self._nodes)

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._nodes

    def __len__(self) -> int:
        return len(self._nodes)

    def __contains__(self, widget: DOMNode) -> bool:
        return widget in self._nodes

    def _append(self, widget: DOMNode) -> None:
        if widget not in self._nodes:
            self._nodes.append(widget)

    def _clear(self) -> None:
        del self._nodes[:]

    def __iter__(self) -> Iterator[DOMNode]:
        return iter(self._nodes)

    @overload
    def __getitem__(self, index: int) -> DOMNode:
        ...

    @overload
    def __getitem__(self, index: slice) -> list[DOMNode]:
        ...

    def __getitem__(self, index: int | slice) -> DOMNode | list[DOMNode]:
        assert self._nodes is not None
        return self._nodes[index]
