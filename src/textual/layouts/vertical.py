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

        x = y = 0
        parent_size = parent.size

        for widget in parent.children:
            styles = widget.styles
            render_width, render_height = parent.size

            render_size, spacing = styles.get_box_model(size, parent_size)

            # TODO:

            if styles.has_rule("width"):
                render_width = int(styles.width.resolve_dimension(size, parent_size))
            if styles.has_rule("height"):
                render_height = int(styles.height.resolve_dimension(size, parent_size))
            region = Region(x, y, render_width, render_height)
            add_placement(WidgetPlacement(region, widget, 0))
            y += render_height

        for placement in placements:
            log(placement)
        return placements, set(parent.children)
