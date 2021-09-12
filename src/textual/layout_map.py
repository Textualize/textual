from __future__ import annotations

from rich.console import Console

from typing import ItemsView, KeysView, ValuesView, NamedTuple

from . import log
from .geometry import Region, Size

from .widget import Widget


class RenderRegion(NamedTuple):
    region: Region
    order: tuple[int, ...]
    clip: Region


class LayoutMap:
    def __init__(self, size: Size) -> None:
        self.size = size
        self.widgets: dict[Widget, RenderRegion] = {}

    def __getitem__(self, widget: Widget) -> RenderRegion:
        return self.widgets[widget]

    def items(self) -> ItemsView[Widget, RenderRegion]:
        return self.widgets.items()

    def keys(self) -> KeysView[Widget]:
        return self.widgets.keys()

    def values(self) -> ValuesView[RenderRegion]:
        return self.widgets.values()

    def clear(self) -> None:
        self.widgets.clear()

    def add_widget(
        self,
        widget: Widget,
        region: Region,
        order: tuple[int, ...],
        clip: Region,
    ) -> None:
        from .view import View

        if widget in self.widgets:
            return

        self.widgets[widget] = RenderRegion(region + widget.layout_offset, order, clip)

        if isinstance(widget, View):
            view: View = widget
            scroll = view.scroll
            total_region = region.size.region
            sub_clip = clip.intersection(region)

            arrangement = view.get_arrangement(region.size, scroll)
            for sub_region, sub_widget, sub_order in arrangement:
                total_region = total_region.union(sub_region)
                if sub_widget is not None:
                    self.add_widget(
                        sub_widget,
                        sub_region + region.origin - scroll,
                        sub_order,
                        sub_clip,
                    )
            view.virtual_size = total_region.size
