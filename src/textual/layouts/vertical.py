from __future__ import annotations

from typing import Iterable

from rich.console import Console


from ..geometry import Offset, Region, Dimensions
from ..layout import Layout
from ..layout_map import LayoutMap
from ..widget import Widget


class VerticalLayout(Layout):
    def __init__(self, *, z: int = 0, gutter: tuple[int, int] | None = None):
        self.z = z
        self.gutter = gutter or (1, 1)
        self._widgets: list[Widget] = []
        super().__init__()

    def add(self, widget: Widget) -> None:
        self._widgets.append(widget)

    def clear(self) -> None:
        del self._widgets[:]

    def get_widgets(self) -> Iterable[Widget]:
        return self._widgets

    def generate_map(
        self, console: Console, size: Dimensions, viewport: Region, scroll: Offset
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
            try:
                region, clip, lines = self.renders[widget]
            except KeyError:
                renderable = widget.render()
                lines = console.render_lines(
                    renderable, console.options.update_width(render_width)
                )

                region = Region(x, y, render_width, len(lines))
                add_widget(widget, region - scroll, viewport)
            else:
                add_widget(
                    widget,
                    Region(x, y, region.width, region.height) - scroll,
                    clip,
                )
                y += region.height + gutter_height

        return map
