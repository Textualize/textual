from __future__ import annotations

from typing import TYPE_CHECKING

from textual.geometry import NULL_OFFSET, Region, Size
from textual.layout import ArrangeResult, Layout, WidgetPlacement

if TYPE_CHECKING:

    from textual.widget import Widget


class StreamLayout(Layout):
    """A cut down version of the vertical layout.

    Faster, but with fewer supported "features".

    """

    name = "stream"

    def arrange(
        self, parent: Widget, children: list[Widget], size: Size, greedy: bool = True
    ) -> ArrangeResult:
        parent.pre_layout(self)
        if not children:
            return []
        viewport = parent.app.size

        _Region = Region
        _WidgetPlacement = WidgetPlacement

        placements: list[WidgetPlacement] = []
        width = size.width
        first_child_styles = children[0].styles
        y = first_child_styles.margin.top
        previous_margin = 0
        null_offset = NULL_OFFSET

        for widget in children:
            styles = widget.styles.base
            margin = styles.margin
            gutter_width, gutter_height = styles.gutter.totals
            top, right, bottom, left = margin
            y += max(top, previous_margin)
            previous_margin = bottom
            height = (
                widget.get_content_height(size, viewport, width - gutter_width)
                + gutter_height
            )
            if (max_height := styles.max_height) is not None and max_height.is_cells:
                height = min(height, int(max_height.value))
            placements.append(
                _WidgetPlacement(
                    _Region(left, y, width - (left + right), height),
                    null_offset,
                    margin,
                    widget,
                    0,
                    False,
                    False,
                    False,
                )
            )
            y += height

        return placements
