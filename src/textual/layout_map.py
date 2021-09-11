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
        self.contents_region = Region(0, 0, 0, 0)
        self.widgets: dict[Widget, RenderRegion] = {}

    @property
    def virtual_size(self) -> Size:
        return self.contents_region.size

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
        self.contents_region = self.contents_region.union(region + widget.layout_offset)

        if isinstance(widget, View):
            widget_placements = list(
                widget.layout.arrange(region.size, clip, widget.scroll)
            )
            total_region = Region(0, 0, 0, 0)
            for placement in widget_placements:
                total_region = total_region.union(placement.region)

            widget.virtual_size = total_region.size
            log(widget, total_region, widget.virtual_size)
            for sub_widget, sub_region, sub_order, sub_clip in widget_placements:
                sub_region += region.origin
                sub_clip = sub_clip.intersection(clip)
                # sub_clip = (sub_clip + region.origin).intersection(clip)
                # sub_clip = sub_clip + region.origin
                self.add_widget(sub_widget, sub_region, sub_order, sub_clip)
