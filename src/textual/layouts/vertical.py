from __future__ import annotations

from rich.console import Console


from ..geometry import Point, Region, Dimensions
from ..layout import Layout
from ..widget import Widget
from ..view import View


class VerticalLayout(Layout):
    def __init__(self, gutter: tuple[int, int] = (0, 1)):
        self.gutter = gutter or (0, 0)
        self._widgets: list[Widget] = []
        super().__init__()

    def add(self, widget: Widget) -> None:
        self._widgets.append(widget)

    def generate_map(
        self, console: Console, size: Dimensions, viewport: Region
    ) -> WidgetMap:
        offset = viewport.origin
        width, height = size
        gutter_width, gutter_height = self.gutter
        render_width = width - gutter_width * 2
        x = gutter_width
        y = gutter_height
        map: dict[Widget, RenderRegion] = {}

        def add_widget(widget: Widget, region: Region):
            order = (0, 0)
            region = region + widget.layout_offset
            map[widget] = RenderRegion(region, order, offset)
            if isinstance(widget, View):
                sub_map = widget.layout.generate_map(
                    console,
                    Dimensions(region.width, region.height),
                    region.origin + offset,
                )
                map.update(sub_map)

        for widget in self._widgets:
            region_lines = self.renders.get(widget)
            if region_lines is None:
                renderable = widget.render()
                lines = console.render_lines(
                    renderable, console.options.update_width(render_width)
                )
                region = Region(x, y, render_width, len(lines))
                add_widget(widget, region)
            else:
                region, lines = region_lines
                add_widget(widget, Region(x, y, region.width, region.height))
                y += region.height + gutter_height
        widget_map = WidgetMap(Dimensions(width, y), map)
        return widget_map
