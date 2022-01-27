from __future__ import annotations

from typing import Iterable

from textual._loop import loop_last
from textual.css.styles import Styles
from textual.geometry import SpacingDimensions, Spacing, Size, Offset, Region
from textual.layout import Layout, WidgetPlacement
from textual.view import View
from textual.widget import Widget


class HorizontalLayout(Layout):
    def __init__(
        self,
        *,
        z: int = 0,
        gutter: SpacingDimensions = (0, 0, 0, 0),
    ):
        self.z = z
        self.gutter = Spacing.unpack(gutter)
        self._max_widget_width = 0
        super().__init__()

    def get_widgets(self, view: View) -> Iterable[Widget]:
        return view.children

    def arrange(
        self, view: View, size: Size, scroll: Offset
    ) -> Iterable[WidgetPlacement]:
        width, height = size
        gutter = self.gutter
        gutter_width = max(gutter.right, gutter.left)
        x, y = self.gutter.top_left

        for last, widget in loop_last(view.children):
            styles: Styles = widget.styles
            render_height = styles.height if styles else height
            if styles.width:
                render_width = int(styles.width.resolve_dimension(size, view.app.size))
            else:
                render_width = width
            region = Region(x, y, render_width, render_height)
            yield WidgetPlacement(region, widget, self.z)
            x += render_width + (gutter.right if last else gutter_width)
