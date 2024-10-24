from __future__ import annotations

from fractions import Fraction
from typing import TYPE_CHECKING

from textual._resolve import resolve_box_models
from textual.geometry import Region, Size
from textual.layout import ArrangeResult, Layout, WidgetPlacement

if TYPE_CHECKING:
    from textual.geometry import Spacing
    from textual.widget import Widget


class HorizontalLayout(Layout):
    """Used to layout Widgets horizontally on screen, from left to right. Since Widgets naturally
    fill the space of their parent container, all widgets used in a horizontal layout should have a specified.
    """

    name = "horizontal"

    def arrange(
        self, parent: Widget, children: list[Widget], size: Size
    ) -> ArrangeResult:
        placements: list[WidgetPlacement] = []
        add_placement = placements.append

        child_styles = [child.styles for child in children]
        box_margins: list[Spacing] = [
            styles.margin for styles in child_styles if styles.overlay != "screen"
        ]
        if box_margins:
            resolve_margin = Size(
                sum(
                    [
                        max(margin1[1], margin2[3])
                        for margin1, margin2 in zip(box_margins, box_margins[1:])
                    ]
                )
                + (box_margins[0].left + box_margins[-1].right),
                max(
                    [
                        margin_top + margin_bottom
                        for margin_top, _, margin_bottom, _ in box_margins
                    ]
                ),
            )
        else:
            resolve_margin = Size(0, 0)

        box_models = resolve_box_models(
            [styles.width for styles in child_styles],
            children,
            size,
            parent.app.size,
            resolve_margin,
            resolve_dimension="width",
        )

        margins = [
            max((box1.margin.right, box2.margin.left))
            for box1, box2 in zip(box_models, box_models[1:])
        ]
        if box_models:
            margins.append(box_models[-1].margin.right)

        x = next(
            (
                Fraction(box_model.margin.left)
                for box_model, child in zip(box_models, children)
                if child.styles.overlay != "screen"
            ),
            Fraction(0),
        )

        _Region = Region
        _WidgetPlacement = WidgetPlacement
        for widget, (content_width, content_height, box_margin), margin in zip(
            children, box_models, margins
        ):
            overlay = widget.styles.overlay == "screen"
            offset_y = box_margin.top
            next_x = x + content_width
            add_placement(
                _WidgetPlacement(
                    _Region(
                        int(x),
                        offset_y,
                        int(next_x - int(x)),
                        int(content_height),
                    ),
                    box_margin,
                    widget,
                    0,
                    False,
                    overlay,
                )
            )
            if not overlay:
                x = next_x + margin

        return placements
