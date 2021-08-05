from __future__ import annotations

from rich.console import Console

from typing import ItemsView, KeysView, ValuesView, NamedTuple

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
        console: Console,
        widget: Widget,
        region: Region,
        order: tuple[int, ...],
        clip: Region,
    ) -> None:
        from .view import View

        region += widget.layout_offset
        self.widgets[widget] = RenderRegion(region, order, clip)
        self.contents_region = self.contents_region.union(region)

        if isinstance(widget, View):
            sub_map = widget.layout.generate_map(
                console, region.size, clip, widget.scroll
            )
            widget.virtual_size = sub_map.virtual_size
            for sub_widget, (sub_region, sub_order, sub_clip) in sub_map.items():
                sub_region += region.origin
                sub_clip = sub_clip.intersection(clip)
                self.add_widget(console, sub_widget, sub_region, sub_order, sub_clip)
