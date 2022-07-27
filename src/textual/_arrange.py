from __future__ import annotations


from fractions import Fraction
from typing import TYPE_CHECKING

from .geometry import Region, Size, Spacing
from ._layout import ArrangeResult, WidgetPlacement
from ._partition import partition


if TYPE_CHECKING:
    from ._layout import ArrangeResult
    from .widget import Widget


def arrange(widget: Widget, size: Size, viewport: Size) -> ArrangeResult:
    display_children = [child for child in widget.children if child.display]

    arrange_widgets: set[Widget] = set()

    dock_layers: dict[str, list[Widget]] = {}
    for child in display_children:
        dock_layers.setdefault(child.styles.layer or "default", []).append(child)

    width, height = size

    placements: list[WidgetPlacement] = []
    add_placement = placements.append
    region = size.region

    _WidgetPlacement = WidgetPlacement

    top_z = 2**32 - 1

    scroll_spacing = Spacing()

    for widgets in dock_layers.values():

        dock_widgets, layout_widgets = partition(
            (lambda widget: not widget.styles.dock), widgets
        )

        arrange_widgets.update(dock_widgets)
        top = right = bottom = left = 0

        for dock_widget in dock_widgets:
            edge = dock_widget.styles.dock

            (
                widget_width_fraction,
                widget_height_fraction,
                margin,
            ) = dock_widget.get_box_model(
                size,
                viewport,
                Fraction(size.height if edge in ("top", "bottom") else size.width),
            )

            widget_width = int(widget_width_fraction) + margin.width
            widget_height = int(widget_height_fraction) + margin.height

            align_offset = dock_widget.styles.align_size(
                (widget_width, widget_height), size
            )

            if edge == "bottom":
                dock_region = Region(
                    0, height - widget_height, widget_width, widget_height
                )
                bottom = max(bottom, dock_region.height)
            elif edge == "top":
                dock_region = Region(0, 0, widget_width, widget_height)
                top = max(top, dock_region.height)
            elif edge == "left":
                dock_region = Region(0, 0, widget_width, widget_height)
                left = max(left, dock_region.width)
            elif edge == "right":
                dock_region = Region(
                    width - widget_width, 0, widget_width, widget_height
                )
                right = max(right, dock_region.width)

            dock_region = dock_region.shrink(margin).translate(align_offset)
            add_placement(_WidgetPlacement(dock_region, dock_widget, top_z, True))

        dock_spacing = Spacing(top, right, bottom, left)
        region = size.region.shrink(dock_spacing)
        layout_placements, _layout_widgets, spacing = widget.layout.arrange(
            widget, layout_widgets, region.size
        )
        if _layout_widgets:
            scroll_spacing = scroll_spacing.grow_maximum(dock_spacing)
            arrange_widgets.update(_layout_widgets)
            placement_offset = region.offset
            if placement_offset:
                layout_placements = [
                    _WidgetPlacement(_region + placement_offset, widget, order, fixed)
                    for _region, widget, order, fixed in layout_placements
                ]

        placements.extend(layout_placements)

    result = ArrangeResult(placements, arrange_widgets, scroll_spacing)
    return result

    # dock_spacing = Spacing(top, right, bottom, left)
    # region = region.shrink(dock_spacing)

    # placements, placement_widgets, spacing = widget.layout.arrange(
    #     widget, layout_widgets, region.size
    # )
    # dock_spacing += spacing

    # placement_offset = region.offset
    # if placement_offset:
    #     placements = [
    #         _WidgetPlacement(_region + placement_offset, widget, order, fixed)
    #         for _region, widget, order, fixed in placements
    #     ]

    # return ArrangeResult(
    #     (dock_placements + placements),
    #     placement_widgets.union(layout_widgets),
    #     dock_spacing,
    # )
