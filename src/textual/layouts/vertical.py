from __future__ import annotations

from typing import Iterable, TYPE_CHECKING

from ..css.styles import Styles
from ..geometry import Offset, Region, Size
from ..layout import Layout, WidgetPlacement

if TYPE_CHECKING:
    from ..widget import Widget
    from ..view import View


class VerticalLayout(Layout):
    def get_widgets(self, view: View) -> Iterable[Widget]:
        return view.children

    def arrange(
        self, view: View, size: Size, scroll: Offset
    ) -> Iterable[WidgetPlacement]:
        parent_width, parent_height = size
        x, y = 0, 0

        for widget in view.children:
            styles: Styles = widget.styles

            if styles.height:
                render_height = int(
                    styles.height.resolve_dimension(size, view.app.size)
                )
            else:
                render_height = size.height

            if styles.width:
                render_width = int(styles.width.resolve_dimension(size, view.app.size))
            else:
                render_width = parent_width

            region = Region(x, y, render_width, render_height)
            yield WidgetPlacement(region, widget, 0)
            y += render_height
