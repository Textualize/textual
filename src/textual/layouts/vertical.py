from __future__ import annotations

from typing import TYPE_CHECKING

from .. import log

from ..geometry import Offset, Region, Size
from ..layout import Layout, WidgetPlacement

if TYPE_CHECKING:
    from ..widget import Widget


class VerticalLayout(Layout):
    """Simple vertical layout."""

    name = "vertical"

    def arrange(
        self, parent: Widget, size: Size, scroll: Offset
    ) -> tuple[list[WidgetPlacement], set[Widget]]:

        placements: list[WidgetPlacement] = []
        add_placement = placements.append

        y = max_width = max_height = 0
        parent_size = parent.size

        for widget in parent.children:
            styles = widget.styles
            (content_width, content_height), margin = styles.get_box_model(
                size, parent_size
            )
            offset_x = styles.align_width(content_width, parent_size.width)

            region = Region(
                margin.left + offset_x, y + margin.top, content_width, content_height
            )
            max_width = max(max_width, content_width + margin.width)
            add_placement(WidgetPlacement(region, widget, 0))
            y += region.height + margin.top
            max_height = y + margin.bottom

        total_region = Region(0, 0, max_width, max_height)
        add_placement(WidgetPlacement(total_region, None, 0))

        return placements, set(parent.children)
