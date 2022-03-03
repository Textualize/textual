from __future__ import annotations

from typing import Iterable


from textual.geometry import Size, Offset, Region
from textual.layout import Layout, WidgetPlacement

from textual.widget import Widget


class HorizontalLayout(Layout):
    """Used to layout Widgets horizontally on screen, from left to right. Since Widgets naturally
    fill the space of their parent container, all widgets used in a horizontal layout should have a specified.
    """

    name = "horizontal"

    def arrange(
        self, parent: Widget, size: Size, scroll: Offset
    ) -> tuple[list[WidgetPlacement], set[Widget]]:

        placements: list[WidgetPlacement] = []
        add_placement = placements.append

        x = y = 0
        app = parent.app
        for widget in parent.children:
            styles = widget.styles
            render_width, render_height = size
            if styles.has_rule("height"):
                render_height = int(styles.height.resolve_dimension(size, app.size))
            if styles.has_rule("width"):
                render_width = int(styles.width.resolve_dimension(size, app.size))
            region = Region(x, y, render_width, render_height)
            add_placement(WidgetPlacement(region, widget, order=0))
            x += render_width

        return placements, set(parent.children)
