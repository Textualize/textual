from __future__ import annotations

from typing import cast

from textual.geometry import Size, Offset, Region
from textual._layout import Layout, WidgetPlacement

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

        box_models = [
            widget.get_box_model(size, parent_size)
            for widget in cast("list[Widget]", parent.children)
        ]

        margins = [
            max((box1.margin.right, box2.margin.left))
            for box1, box2 in zip(box_models, box_models[1:])
        ]
        if box_models:
            margins.append(box_models[-1].margin.right)

        x = box_models[0].margin.left if box_models else 0

        for widget, box_model, margin in zip(parent.children, box_models, margins):
            content_width, content_height = box_model.size
            offset_y = widget.styles.align_height(content_height, parent_size.height)
            region = Region(x, offset_y, content_width, content_height)
            max_height = max(max_height, content_height)
            add_placement(WidgetPlacement(region, widget, 0))
            x += region.width + margin
            max_width = x

        max_width += margins[-1] if margins else 0

        total_region = Region(0, 0, max_width, max_height)
        add_placement(WidgetPlacement(total_region, None, 0))

        return placements, set(parent.children)
