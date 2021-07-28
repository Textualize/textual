from __future__ import annotations

from rich.console import Console

from typing import ItemsView, KeysView, ValuesView, NamedTuple

from .geometry import Region, Dimensions

from .widget import Widget


class RenderRegion(NamedTuple):
    region: Region
    order: tuple[int, ...]
    clip: Region


class LayoutMap:
    def __init__(self, size: Dimensions) -> None:
        self.region = size.region
        self.widgets: dict[Widget, RenderRegion] = {}

    @property
    def size(self) -> Dimensions:
        return self.region.size

    def __getitem__(self, widget: Widget) -> RenderRegion:
        return self.widgets[widget]

    def items(self) -> ItemsView:
        return self.widgets.items()

    def keys(self) -> KeysView:
        return self.widgets.keys()

    def values(self) -> ValuesView:
        return self.widgets.values()

    def clear(self) -> None:
        self.widgets.clear()

    def add_widget(
        self,
        console: Console,
        widget: Widget,
        region: Region,
        order: tuple[int, ...],
        clip: Region,
    ) -> None:
        from .view import View

        region += widget.layout_offset
        self.widgets[widget] = RenderRegion(region, order, clip)
        self.region = self.region.union(region.intersection(clip))

        if isinstance(widget, View):
            sub_map = widget.layout.generate_map(
                console, region.size, region, widget.scroll
            )
            for widget, (sub_region, sub_order, sub_clip) in sub_map.items():
                sub_region += region.origin
                sub_clip = sub_clip.intersection(clip)
                self.add_widget(console, widget, sub_region, sub_order, sub_clip)
