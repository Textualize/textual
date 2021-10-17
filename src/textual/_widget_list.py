from __future__ import annotations

from typing import Iterable, overload, TYPE_CHECKING
from weakref import ref

import rich.repr

if TYPE_CHECKING:
    from .widget import Widget


@rich.repr.auto
class WidgetList:
    """
    A container for widgets that forms one level of hierarchy.

    Although named a list, widgets may appear only once, making them more like a set.

    """

    def __init__(self) -> None:
        self._widget_refs: list[ref[Widget]] = []
        self.__widgets: list[Widget] | None = []

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._widgets

    def __len__(self) -> int:
        return len(self._widgets)

    def __contains__(self, widget: Widget) -> bool:
        return widget in self._widgets

    @property
    def _widgets(self) -> list[Widget]:
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

    def _append(self, widget: Widget):
        if widget not in self._widgets:
            self._widget_refs.append(ref(widget))
            self.__widgets = None

    def _clear(self) -> None:
        del self._widget_refs[:]
        self.__widgets = None

    def __iter__(self) -> Iterable[Widget]:
        for widget_ref in self._widget_refs:
            widget = widget_ref()
            if widget is not None:
                yield widget

    @overload
    def __getitem__(self, index: int) -> Widget:
        ...

    @overload
    def __getitem__(self, index: slice) -> list[Widget]:
        ...

    def __getitem__(self, index: int | slice) -> Widget | list[Widget]:
        self._prune()
        assert self._widgets is not None
        return self._widgets[index]
