from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from operator import attrgetter
from typing import TYPE_CHECKING, Iterable, Mapping, Sequence

from ._layout import DockArrangeResult, WidgetPlacement
from ._partition import partition
from .geometry import Region, Size, Spacing

if TYPE_CHECKING:
    from .widget import Widget

# TODO: This is a bit of a fudge, need to ensure it is impossible for layouts to generate this value
TOP_Z = 2**31 - 1


def _build_dock_layers(widgets: Iterable[Widget]) -> Mapping[str, Sequence[Widget]]:
    """Organize widgets into layers.

    Args:
        widgets: The widgets.

    Returns:
        A mapping of layer name onto the widgets within the layer.
    """
    layers: defaultdict[str, list[Widget]] = defaultdict(list)
    for widget in widgets:
        layers[widget.layer].append(widget)
    return layers


def arrange(
    widget: Widget, children: Sequence[Widget], size: Size, viewport: Size
) -> DockArrangeResult:
    """Arrange widgets by applying docks and calling layouts

    Args:
        widget: The parent (container) widget.
        size: The size of the available area.
        viewport: The size of the viewport (terminal).

    Returns:
        Widget arrangement information.
    """

    placements: list[WidgetPlacement] = []
    scroll_spacing = Spacing()
    get_dock = attrgetter("styles.dock")
    styles = widget.styles

    # Widgets which will be displayed
    display_widgets = [child for child in children if child.styles.display != "none"]

    # Widgets organized into layers
    dock_layers = _build_dock_layers(display_widgets)

    layer_region = size.region
    for widgets in dock_layers.values():
        region = layer_region

        # Partition widgets into "layout" widgets (those that appears in the normal 'flow' of the
        # document), and "dock" widgets which are positioned relative to an edge
        layout_widgets, dock_widgets = partition(get_dock, widgets)

        # Arrange docked widgets
        _dock_placements, dock_spacing = _arrange_dock_widgets(
            dock_widgets, size, viewport
        )
        placements.extend(_dock_placements)

        # Reduce the region to compensate for docked widgets
        region = region.shrink(dock_spacing)

        if layout_widgets:
            # Arrange layout widgets (i.e. not docked)
            layout_placements = widget._layout.arrange(
                widget,
                layout_widgets,
                region.size,
            )

            scroll_spacing = scroll_spacing.grow_maximum(dock_spacing)

            placement_offset = region.offset
            # Perform any alignment of the widgets.
            if styles.align_horizontal != "left" or styles.align_vertical != "top":
                bounding_region = WidgetPlacement.get_bounds(layout_placements)
                placement_offset += styles._align_size(
                    bounding_region.size, region.size
                ).clamped

            if placement_offset:
                # Translate placements if required.
                layout_placements = WidgetPlacement.translate(
                    layout_placements, placement_offset
                )

            placements.extend(layout_placements)

    return DockArrangeResult(placements, set(display_widgets), scroll_spacing)


def _arrange_dock_widgets(
    dock_widgets: Sequence[Widget], size: Size, viewport: Size
) -> tuple[list[WidgetPlacement], Spacing]:
    """Arrange widgets which are *docked*.

    Args:
        dock_widgets: Widgets with a non-empty dock.
        size: Size of the container.
        viewport: Size of the viewport.

    Returns:
        A tuple of widget placements, and additional spacing around them
    """
    _WidgetPlacement = WidgetPlacement
    top_z = TOP_Z
    width, height = size
    null_spacing = Spacing()

    top = right = bottom = left = 0

    placements: list[WidgetPlacement] = []
    append_placement = placements.append

    for dock_widget in dock_widgets:
        edge = dock_widget.styles.dock

        box_model = dock_widget._get_box_model(
            size, viewport, Fraction(size.width), Fraction(size.height)
        )
        widget_width_fraction, widget_height_fraction, margin = box_model

        widget_width = int(widget_width_fraction) + margin.width
        widget_height = int(widget_height_fraction) + margin.height

        if edge == "bottom":
            dock_region = Region(0, height - widget_height, widget_width, widget_height)
            bottom = max(bottom, widget_height)
        elif edge == "top":
            dock_region = Region(0, 0, widget_width, widget_height)
            top = max(top, widget_height)
        elif edge == "left":
            dock_region = Region(0, 0, widget_width, widget_height)
            left = max(left, widget_width)
        elif edge == "right":
            dock_region = Region(width - widget_width, 0, widget_width, widget_height)
            right = max(right, widget_width)
        else:
            # Should not occur, mainly to keep Mypy happy
            raise AssertionError("invalid value for edge")  # pragma: no-cover

        align_offset = dock_widget.styles._align_size(
            (widget_width, widget_height), size
        )
        dock_region = dock_region.shrink(margin).translate(align_offset)
        append_placement(
            _WidgetPlacement(dock_region, null_spacing, dock_widget, top_z, True)
        )
    dock_spacing = Spacing(top, right, bottom, left)
    return (placements, dock_spacing)
