from __future__ import annotations

from typing import Iterable

from textual._loop import loop_last
from textual.css.styles import Styles
from textual.geometry import Size, Offset, Region
from textual.layout import Layout, WidgetPlacement
from textual.view import View
from textual.widget import Widget


class HorizontalLayout(Layout):
    """Used to layout Widgets horizontally on screen, from left to right. Since Widgets naturally
    fill the space of their parent container, all widgets used in a horizontal layout should have a specified.
    """

    def get_widgets(self, view: View) -> Iterable[Widget]:
        return view.children

    def arrange(
        self, view: View, size: Size, scroll: Offset
    ) -> Iterable[WidgetPlacement]:
        parent_width, parent_height = size
        x, y = 0, 0
        for last, widget in loop_last(view.children):
            styles: Styles = widget.styles
            if styles.height:
                render_height = int(
                    styles.height.resolve_dimension(size, view.app.size)
                )
            else:
                render_height = parent_height
            if styles.width:
                render_width = int(styles.width.resolve_dimension(size, view.app.size))
            else:
                render_width = parent_width
            region = Region(x, y, render_width, render_height)
            yield WidgetPlacement(region, widget, order=0)
            x += render_width
