from __future__ import annotations

from typing import Iterable, TYPE_CHECKING

from ..css.styles import Styles
from ..geometry import Offset, Region, Size
from ..layout import Layout, WidgetPlacement

if TYPE_CHECKING:
    from ..widget import Widget
    from ..screen import Screen


class VerticalLayout(Layout):
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
                render_height = size.height

            if styles.width:
                render_width = int(styles.width.resolve_dimension(size, app.size))
            else:
                render_width = parent_width

            region = Region(x, y, render_width, render_height)
            add_placement(WidgetPlacement(region, widget, 0))
            y += render_height

        return placements, set(parent.children)
