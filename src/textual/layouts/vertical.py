from __future__ import annotations

from typing import Iterable

from ..geometry import Offset, Region, Size
from ..layout import Layout, WidgetPlacement
from ..widget import Widget


class VerticalLayout(Layout):
    def __init__(
        self,
        *,
        auto_width: bool = False,
        z: int = 0,
        gutter: tuple[int, int] | None = None
    ):
        self.auto_width = auto_width
        self.z = z
        self.gutter = gutter or (0, 0)
        self._widgets: list[Widget] = []
        self._max_widget_width = 0
        super().__init__()

    def add(self, widget: Widget) -> None:
        self._widgets.append(widget)
        self._max_widget_width = max(widget.app.measure(widget), self._max_widget_width)

    def clear(self) -> None:
        del self._widgets[:]
        self._max_widget_width = 0

    def get_widgets(self) -> Iterable[Widget]:
        return self._widgets

    def arrange(self, size: Size, scroll: Offset) -> Iterable[WidgetPlacement]:
        index = 0
        width, _height = size
        gutter_height, gutter_width = self.gutter
        render_width = (
            max(width, self._max_widget_width) + gutter_width * 2
            if self.auto_width
            else width - gutter_width * 2
        )

        x = gutter_width
        y = gutter_height

        total_region = Region()
        for widget in self._widgets:
            if (
                not widget.render_cache
                or widget.render_cache.size.width != render_width
            ):
                widget.render_lines_free(render_width)
            assert widget.render_cache is not None
            render_height = widget.render_cache.size.height
            region = Region(x, y, render_width, render_height)
            yield WidgetPlacement(region, widget, (self.z, index))
            total_region = total_region.union(region)

        yield WidgetPlacement(total_region)
