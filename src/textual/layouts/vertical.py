from __future__ import annotations

from typing import Iterable

from ..geometry import Offset, Region, Size, Spacing, SpacingDimensions
from ..layout import Layout, WidgetPlacement
from ..widget import Widget
from .._loop import loop_last


class VerticalLayout(Layout):
    def __init__(
        self,
        *,
        auto_width: bool = False,
        z: int = 0,
        gutter: SpacingDimensions = (0, 0, 0, 0),
    ):
        self.auto_width = auto_width
        self.z = z
        self.gutter = Spacing.unpack(gutter)
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
        gutter = self.gutter
        x, y = self.gutter.top_left
        render_width = (
            max(width, self._max_widget_width)
            if self.auto_width
            else width - gutter.width
        )

        total_width = render_width

        gutter_height = max(gutter.top, gutter.bottom)

        for last, widget in loop_last(self._widgets):
            if (
                not widget.render_cache
                or widget.render_cache.size.width != render_width
            ):
                widget.render_lines_free(render_width)
            assert widget.render_cache is not None
            render_height = widget.render_cache.size.height
            region = Region(x, y, render_width, render_height)
            yield WidgetPlacement(region, widget, (self.z, index))
            y += render_height + (gutter.bottom if last else gutter_height)

        yield WidgetPlacement(Region(0, 0, total_width + gutter.width, y))
