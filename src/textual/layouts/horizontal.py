from __future__ import annotations

from typing import Iterable

from textual._loop import loop_last
from textual.css.styles import Styles
from textual.geometry import Size, Offset, Region
from textual.layout import Layout, WidgetPlacement
from textual.screen import Screen
from textual.widget import Widget


class HorizontalLayout(Layout):
    """Used to layout Widgets horizontally on screen, from left to right. Since Widgets naturally
    fill the space of their parent container, all widgets used in a horizontal layout should have a specified.
    """

    def arrange(
        self, parent: Widget, size: Size, scroll: Offset
    ) -> tuple[list[WidgetPlacement], set[Widget]]:

        placements: list[WidgetPlacement] = []
        add_placement = placements.append

        parent_width, parent_height = size
        x = y = 0
        app = parent.app
        for widget in parent.children:
            styles = widget.styles

            if styles.height:
                render_height = int(styles.height.resolve_dimension(size, app.size))
            else:
                render_height = parent_height
            if styles.width:
                render_width = int(styles.width.resolve_dimension(size, app.size))
            else:
                render_width = parent_width
            region = Region(x, y, render_width, render_height)
            add_placement(WidgetPlacement(region, widget, order=0))
            x += render_width

        return placements, set(parent.children)
