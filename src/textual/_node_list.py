from __future__ import annotations

from typing import Iterator, overload, TYPE_CHECKING
from weakref import ref

import rich.repr

if TYPE_CHECKING:
    from .widget import Widget
    from .dom import DOMNode


@rich.repr.auto
class NodeList:
    """
    A container for widgets that forms one level of hierarchy.

    Although named a list, widgets may appear only once, making them more like a set.

    """

    def __init__(self) -> None:
        self._widget_refs: list[ref[DOMNode]] = []
        self.__widgets: list[DOMNode] | None = []

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._widgets

    def __len__(self) -> int:
        return len(self._widgets)

    def __contains__(self, widget: Widget) -> bool:
        return widget in self._widgets

    @property
    def _widgets(self) -> list[DOMNode]:
        if self.__widgets is None:
            self.__widgets = list(
                filter(None, [widget_ref() for widget_ref in self._widget_refs])
            )
        return self.__widgets

    def _prune(self) -> None:
        """Remove expired references."""
        self._widget_refs[:] = filter(
            None,
            [
                None if widget_ref() is None else widget_ref
                for widget_ref in self._widget_refs
            ],
        )

    def _append(self, widget: DOMNode) -> None:
        if widget not in self._widgets:
            self._widget_refs.append(ref(widget))
            self.__widgets = None

    def _clear(self) -> None:
        del self._widget_refs[:]
        self.__widgets = None

    def __iter__(self) -> Iterator[DOMNode]:
        for widget_ref in self._widget_refs:
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
