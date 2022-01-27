from __future__ import annotations

from typing import Iterable, TYPE_CHECKING

from textual import log
from ..css.styles import Styles
from ..geometry import Offset, Region, Size, Spacing, SpacingDimensions
from ..layout import Layout, WidgetPlacement
from .._loop import loop_last

if TYPE_CHECKING:
    from ..widget import Widget
    from ..view import View


class VerticalLayout(Layout):
    def __init__(
        self,
        *,
        auto_width: bool = False,
        z: int = 0,
        gutter: SpacingDimensions = (0, 0, 0, 0)
    ):
        self.auto_width = auto_width
        self.z = z
        self.gutter = Spacing.unpack(gutter)
        self._max_widget_width = 0
        super().__init__()

    def get_widgets(self, view: View) -> Iterable[Widget]:
        return view.children

    def arrange(
        self, view: View, size: Size, scroll: Offset
    ) -> Iterable[WidgetPlacement]:
        width, _height = size
        gutter = self.gutter
        x, y = self.gutter.top_left
        render_width = (
            max(width, self._max_widget_width)
            if self.auto_width
            else width - gutter.width
        )

        total_width = render_width
        gutter_height = max(gutter.top, gutter.bottom)

        for last, widget in loop_last(view.children):
            styles: Styles = widget.styles
            if styles.height:
                render_height = int(
                    styles.height.resolve_dimension(size, view.app.size)
                )
            else:
                render_height = size.height
            if styles.width:
                render_width = min(styles.width.cells, render_width)
            region = Region(x, y, render_width, render_height)
            yield WidgetPlacement(region, widget, self.z)
            y += render_height + (gutter.bottom if last else gutter_height)

        yield WidgetPlacement(Region(0, 0, total_width + gutter.width, y))
