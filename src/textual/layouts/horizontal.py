from __future__ import annotations

from fractions import Fraction

from .._resolve import resolve_box_models
from ..geometry import Size, Region
from .._layout import ArrangeResult, Layout, WidgetPlacement
from ..widget import Widget


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
        x = max_height = Fraction(0)
        parent_size = parent.outer_size

        box_models = resolve_box_models(
            [child.styles.width for child in children],
            children,
            size,
            parent_size,
            dimension="width",
        )

        margins = [
            max((box1.margin.right, box2.margin.left))
            for box1, box2 in zip(box_models, box_models[1:])
        ]
        if box_models:
            margins.append(box_models[-1].margin.right)

        x = Fraction(box_models[0].margin.left if box_models else 0)

        displayed_children = [child for child in children if child.display]

        _Region = Region
        _WidgetPlacement = WidgetPlacement
        for widget, box_model, margin in zip(children, box_models, margins):
            content_width, content_height, box_margin = box_model
            offset_y = box_margin.top
            next_x = x + content_width
            region = _Region(
                int(x), offset_y, int(next_x - int(x)), int(content_height)
            )
            max_height = max(
                max_height, content_height + offset_y + box_model.margin.bottom
            )
            add_placement(_WidgetPlacement(region, box_model.margin, widget, 0))
            x = next_x + margin

        return placements, set(displayed_children)

    def get_content_width(self, widget: Widget, container: Size, viewport: Size) -> int:
        """Get the width of the content. In Horizontal layout, the content width of
        a widget is the sum of the widths of its children.

        Args:
            widget (Widget): The container widget.
            container (Size): The container size.
            viewport (Size): The viewport size.

        Returns:
            int: Width of the content.
        """
        width: int | None = None
        gutter_width = widget.gutter.width
        for child in widget.displayed_children:
            if not child.is_container:
                child_width = (
                    child.get_content_width(container, viewport)
                    + gutter_width
                    + child.gutter.width
                )
                if width is None:
                    width = child_width
                else:
                    width += child_width
        if width is None:
            width = container.width

        return width
