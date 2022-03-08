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

        # placements: list[WidgetPlacement] = []
        # add_placement = placements.append

        # x = y = 0
        # app = parent.app
        # for widget in parent.children:
        #     styles = widget.styles
        #     render_width, render_height = size
        #     if styles.has_rule("height"):
        #         render_height = int(styles.height.resolve_dimension(size, app.size))
        #     if styles.has_rule("width"):
        #         render_width = int(styles.width.resolve_dimension(size, app.size))
        #     region = Region(x, y, render_width, render_height)
        #     add_placement(WidgetPlacement(region, widget, order=0))
        #     x += render_width

        # return placements, set(parent.children)

        placements: list[WidgetPlacement] = []
        add_placement = placements.append

        x = max_width = max_height = 0
        parent_size = parent.size

        for widget in parent.children:

            (content_width, content_height), margin = widget.styles.get_box_model(
                size, parent_size
            )

            region = Region(margin.left + x, margin.top, content_width, content_height)
            max_height = max(max_height, content_height + margin.height)
            add_placement(WidgetPlacement(region, widget, 0))
            x += region.x_max
            max_width = x + margin.right

        total_region = Region(0, 0, max_width, max_height)
        add_placement(WidgetPlacement(total_region, None, 0))

        return placements, set(parent.children)
