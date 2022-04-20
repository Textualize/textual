from __future__ import annotations


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

        x = max_width = max_height = 0
        parent_size = parent.size

        for widget in parent.children:
            styles = widget.styles
            (content_width, content_height), margin = widget.get_box_model(
                size, parent_size
            )
            offset_y = styles.align_height(
                content_height + margin.height, parent_size.height
            )
            region = Region(
                margin.left + x, margin.top + offset_y, content_width, content_height
            )
            max_height = max(max_height, content_height + margin.height)
            add_placement(WidgetPlacement(region, widget, 0))
            x += region.width + margin.left
            max_width = x + margin.right

        total_region = Region(0, 0, max_width, max_height)
        add_placement(WidgetPlacement(total_region, None, 0))

        return placements, set(parent.children)
