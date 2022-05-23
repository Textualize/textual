from __future__ import annotations

from typing import cast, TYPE_CHECKING

from ..geometry import Region, Size
from .._layout import ArrangeResult, Layout, WidgetPlacement

if TYPE_CHECKING:
    from ..widget import Widget


class VerticalLayout(Layout):
    """Used to layout Widgets vertically on screen, from top to bottom."""

    name = "vertical"

    def arrange(self, parent: Widget, size: Size) -> ArrangeResult:

        placements: list[WidgetPlacement] = []
        add_placement = placements.append

        parent_size = parent.size

        box_models = [
            widget.get_box_model(size, parent_size)
            for widget in cast("list[Widget]", parent.children)
        ]

        margins = [
            max((box1.margin.bottom, box2.margin.top))
            for box1, box2 in zip(box_models, box_models[1:])
        ]
        if box_models:
            margins.append(box_models[-1].margin.bottom)

        y = box_models[0].margin.top if box_models else 0

        displayed_children = cast("list[Widget]", parent.displayed_children)
        for widget, box_model, margin in zip(displayed_children, box_models, margins):
            content_width, content_height = box_model.size
            offset_x = (
                widget.styles.align_width(
                    content_width, size.width - box_model.margin.width
                )
                + box_model.margin.left
            )
            region = Region(offset_x, y, content_width, content_height)
            add_placement(WidgetPlacement(region, widget, 0))
            y += region.height + margin

        total_region = Region(0, 0, size.width, y)
        add_placement(WidgetPlacement(total_region, None, 0))

        return placements, set(displayed_children)
