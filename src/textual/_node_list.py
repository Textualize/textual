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
        self._node_refs: list[ref[DOMNode]] = []
        self.__nodes: list[DOMNode] | None = []

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._widgets

    def __len__(self) -> int:
        return len(self._widgets)

    def __contains__(self, widget: DOMNode) -> bool:
        return widget in self._widgets

    @property
    def _widgets(self) -> list[DOMNode]:
        if self.__nodes is None:
            self.__nodes = list(
                filter(None, [widget_ref() for widget_ref in self._node_refs])
            )
        return self.__nodes

    def _prune(self) -> None:
        """Remove expired references."""
        self._node_refs[:] = filter(
            None,
            [
                None if widget_ref() is None else widget_ref
                for widget_ref in self._node_refs
            ],
        )

    def _append(self, widget: DOMNode) -> None:
        if widget not in self._widgets:
            self._node_refs.append(ref(widget))
            self.__nodes = None

    def _clear(self) -> None:
        del self._node_refs[:]
        self.__nodes = None

    def __iter__(self) -> Iterator[DOMNode]:
        for widget_ref in self._node_refs:
            widget = widget_ref()
            if widget is not None:
                yield widget

    @overload
    def __getitem__(self, index: int) -> DOMNode:
        ...

    @overload
    def __getitem__(self, index: slice) -> list[DOMNode]:
        ...

    def __getitem__(self, index: int | slice) -> DOMNode | list[DOMNode]:
        self._prune()
        assert self._widgets is not None
        return self._widgets[index]
