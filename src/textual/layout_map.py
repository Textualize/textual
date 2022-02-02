from __future__ import annotations


from typing import ItemsView, KeysView, ValuesView, NamedTuple

from . import log
from .geometry import Offset, Region, Size
from operator import attrgetter
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

        layout_offset = Offset(0, 0)
        if any(widget.styles.offset):
            layout_offset = widget.styles.offset.resolve(region.size, clip.size)

        self.widgets[widget] = RenderRegion(region + layout_offset, order, clip)

        if isinstance(widget, View):
            view: View = widget
            scroll = view.scroll
            total_region = region.size.region
            sub_clip = clip.intersection(region)

            arrangement = sorted(
                view.get_arrangement(region.size, scroll), key=attrgetter("order")
            )
            for sub_region, sub_widget, z in arrangement:
                total_region = total_region.union(sub_region)
                if sub_widget is not None:
                    self.add_widget(
                        sub_widget,
                        sub_region + region.origin - scroll,
                        sub_widget.z + (z,),
                        sub_clip,
                    )
            view.virtual_size = total_region.size
