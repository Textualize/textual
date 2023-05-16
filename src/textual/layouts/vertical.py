from __future__ import annotations

from fractions import Fraction
from typing import TYPE_CHECKING

from .._layout import ArrangeResult, Layout, WidgetPlacement
from .._resolve import resolve_box_models
from ..geometry import Region, Size

if TYPE_CHECKING:
    from ..geometry import Spacing
    from ..widget import Widget


class VerticalLayout(Layout):
    """Used to layout Widgets vertically on screen, from top to bottom."""

    name = "vertical"

    def arrange(
        self, parent: Widget, children: list[Widget], size: Size
    ) -> ArrangeResult:
        placements: list[WidgetPlacement] = []
        add_placement = placements.append

        child_styles = [child.styles for child in children]
        box_margins: list[Spacing] = [styles.margin for styles in child_styles]
        if box_margins:
            resolve_margin = Size(
                max(
                    [
                        margin_right + margin_left
                        for _, margin_right, _, margin_left in box_margins
                    ]
                ),
                sum(
                    [
                        max(margin1[2], margin2[0])
                        for margin1, margin2 in zip(box_margins, box_margins[1:])
                    ]
                )
                + (box_margins[0].top + box_margins[-1].bottom),
            )
        else:
            resolve_margin = Size(0, 0)

        box_models = resolve_box_models(
            [styles.height for styles in child_styles],
            children,
            size,
            parent.app.size,
            resolve_margin,
            resolve_dimension="height",
        )

        margins = [
            max((box1.margin.bottom, box2.margin.top))
            for box1, box2 in zip(box_models, box_models[1:])
        ]
        if box_models:
            margins.append(box_models[-1].margin.bottom)

        y = Fraction(box_models[0].margin.top if box_models else 0)

        _Region = Region
        _WidgetPlacement = WidgetPlacement

        for widget, box_model, margin in zip(children, box_models, margins):
            overlay = widget.styles.overlay == "screen"
            content_width, content_height, box_margin = box_model
            next_y = y + content_height

            region = _Region(
                box_margin.left, int(y), int(content_width), int(next_y) - int(y)
            )
            add_placement(
                _WidgetPlacement(
                    region,
                    box_model.margin,
                    widget,
                    0,
                    False,
                    overlay,
                )
            )
            if not overlay:
                y = next_y + margin

        return placements
