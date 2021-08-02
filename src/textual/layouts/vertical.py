from __future__ import annotations

from typing import Iterable

from rich.console import Console

from .. import log
from ..geometry import Offset, Region, Size
from ..layout import Layout
from ..layout_map import LayoutMap
from ..widget import Widget


class VerticalLayout(Layout):
    def __init__(self, *, z: int = 0, gutter: tuple[int, int] | None = None):
        self.z = z
        self.gutter = gutter or (0, 0)
        self._widgets: list[Widget] = []
        super().__init__()

    def add(self, widget: Widget) -> None:
        self._widgets.append(widget)

    def clear(self) -> None:
        del self._widgets[:]

    def get_widgets(self) -> Iterable[Widget]:
        return self._widgets

    def generate_map(
        self, console: Console, size: Size, viewport: Region, scroll: Offset
    ) -> LayoutMap:
        index = 0
        width, height = size
        gutter_width, gutter_height = self.gutter
        render_width = width - gutter_width * 2
        x = gutter_width
        y = gutter_height
        map: LayoutMap = LayoutMap(size)

        def add_widget(widget: Widget, region: Region, clip: Region) -> None:
            map.add_widget(console, widget, region, (self.z, index), clip)

        for widget in self._widgets:
            # if widget._render_cache is not None:
            #     lines = widget._render_cache.lines
            # else:
            #     lines = widget.render_lines(render_width).lines

            region = Region(x, y, render_width, 100)
            add_widget(widget, region - scroll, viewport)

            # try:
            #     region, clip = self.regions[widget]
            # except KeyError:
            #     lines = widget.render_lines(render_width)
            #     log("***VERTICAL", len(lines))
            #     region = Region(x, y, render_width, len(lines))
            #     add_widget(widget, region - scroll, viewport)
            # else:
            #     add_widget(
            #         widget, Region(x, y, region.width, region.height) - scroll, clip
            #     )
            #     y += region.height + gutter_height

        return map
