from __future__ import annotations

from typing import TYPE_CHECKING

from textual.geometry import NULL_OFFSET, Region, Size
from textual.layout import ArrangeResult, Layout, WidgetPlacement

if TYPE_CHECKING:

    from textual.widget import Widget


class StreamLayout(Layout):
    name = "stream"

    def arrange(
        self, parent: Widget, children: list[Widget], size: Size, greedy: bool = True
    ) -> ArrangeResult:
        parent.pre_layout(self)
        viewport = parent.app.size

        placements: list[WidgetPlacement] = []
        if not children:
            return []
        width = size.width
        first_child_styles = children[0].styles
        y = first_child_styles.margin.top
        previous_margin = 0
        null_offset = NULL_OFFSET

        for widget in children:
            styles = widget.styles
            overlay = styles.overlay == "screen"
            absolute = styles.has_rule("position") and styles.position == "absolute"
            margin = styles.margin
            top, right, bottom, left = margin
            margin_width = left + right
            y += max(top, previous_margin)
            previous_margin = bottom
            height = widget.get_content_height(size, viewport, width - margin_width)
            height += styles.gutter.height
            if (max_height := styles.max_height) is not None and max_height.is_cells:
                height = min(height, int(max_height.value))
            placements.append(
                WidgetPlacement(
                    Region(left, y, width - margin_width, height),
                    null_offset,
                    margin,
                    widget,
                    0,
                    False,
                    overlay,
                    absolute,
                )
            )
            y += height

        return placements
