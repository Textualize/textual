from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from operator import attrgetter
from typing import TYPE_CHECKING, Iterable, Mapping, Sequence

from textual._partition import partition
from textual.geometry import NULL_OFFSET, NULL_SPACING, Region, Size, Spacing
from textual.layout import DockArrangeResult, WidgetPlacement

if TYPE_CHECKING:
    from textual.widget import Widget

# TODO: This is a bit of a fudge, need to ensure it is impossible for layouts to generate this value
TOP_Z = 2**31 - 1


def _build_layers(widgets: Iterable[Widget]) -> Mapping[str, Sequence[Widget]]:
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
    widget: Widget,
    children: Sequence[Widget],
    size: Size,
    viewport: Size,
    optimal: bool = False,
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

    get_dock = attrgetter("styles.is_docked")
    get_split = attrgetter("styles.is_split")
    get_display = attrgetter("styles.display")

    styles = widget.styles

    # Widgets which will be displayed
    display_widgets = [child for child in children if get_display(child) != "none"]
    # Widgets organized into layers
    layers = _build_layers(display_widgets)

    for widgets in layers.values():
        # Partition widgets into split widgets and non-split widgets
        non_split_widgets, split_widgets = partition(get_split, widgets)
        if split_widgets:
            _split_placements, dock_region = _arrange_split_widgets(
                split_widgets, size, viewport
            )
            placements.extend(_split_placements)
        else:
            dock_region = size.region

        split_spacing = size.region.get_spacing_between(dock_region)

        # Partition widgets into "layout" widgets (those that appears in the normal 'flow' of the
        # document), and "dock" widgets which are positioned relative to an edge
        layout_widgets, dock_widgets = partition(get_dock, non_split_widgets)

        # Arrange docked widgets
        if dock_widgets:
            _dock_placements, dock_spacing = _arrange_dock_widgets(
                dock_widgets, dock_region, viewport, greedy=not optimal
            )
            placements.extend(_dock_placements)
            dock_region = dock_region.shrink(dock_spacing)
        else:
            dock_spacing = Spacing()

        dock_spacing += split_spacing

        if layout_widgets:
            # Arrange layout widgets (i.e. not docked)
            layout_placements = widget.layout.arrange(
                widget, layout_widgets, dock_region.size, greedy=not optimal
            )
            scroll_spacing = scroll_spacing.grow_maximum(dock_spacing)
            placement_offset = dock_region.offset
            # Perform any alignment of the widgets.
            if styles.align_horizontal != "left" or styles.align_vertical != "top":
                bounding_region = WidgetPlacement.get_bounds(layout_placements)
                container_width, container_height = dock_region.size
                placement_offset += styles._align_size(
                    bounding_region.size,
                    widget._extrema.apply_dimensions(
                        0 if styles.is_auto_width else container_width,
                        0 if styles.is_auto_height else container_height,
                    ),
                ).clamped

            if placement_offset:
                # Translate placements if required.
                layout_placements = WidgetPlacement.translate(
                    layout_placements, placement_offset
                )

            WidgetPlacement.apply_absolute(layout_placements)
            placements.extend(layout_placements)

    return DockArrangeResult(placements, set(display_widgets), scroll_spacing)


def _arrange_dock_widgets(
    dock_widgets: Sequence[Widget], region: Region, viewport: Size, greedy: bool = True
) -> tuple[list[WidgetPlacement], Spacing]:
    """Arrange widgets which are *docked*.

    Args:
        dock_widgets: Widgets with a non-empty dock.
        region: Region to dock within.
        viewport: Size of the viewport.

    Returns:
        A tuple of widget placements, and additional spacing around them.
    """
    _WidgetPlacement = WidgetPlacement
    top_z = TOP_Z
    region_offset = region.offset
    size = region.size
    width, height = size
    null_spacing = NULL_SPACING

    top = right = bottom = left = 0

    placements: list[WidgetPlacement] = []
    append_placement = placements.append

    for dock_widget in dock_widgets:
        edge = dock_widget.styles.dock

        box_model = dock_widget._get_box_model(
            size, viewport, Fraction(size.width), Fraction(size.height), greedy=greedy
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
            raise AssertionError("invalid value for dock edge")  # pragma: no-cover

        dock_region = dock_region.shrink(margin)
        styles = dock_widget.styles
        offset = (
            styles.offset.resolve(
                size,
                viewport,
            )
            if styles.has_rule("offset")
            else NULL_OFFSET
        )
        append_placement(
            _WidgetPlacement(
                dock_region.translate(region_offset),
                offset,
                null_spacing,
                dock_widget,
                top_z,
                True,
                False,
            )
        )

    dock_spacing = Spacing(top, right, bottom, left)
    return (placements, dock_spacing)


def _arrange_split_widgets(
    split_widgets: Sequence[Widget], size: Size, viewport: Size
) -> tuple[list[WidgetPlacement], Region]:
    """Arrange split widgets.

    Split widgets are "docked" but also reduce the area available for regular widgets.

    Args:
        split_widgets: Widgets to arrange.
        size: Available area to arrange.
        viewport: Viewport (size of terminal).

    Returns:
        A tuple of widget placements, and the remaining view area.
    """
    _WidgetPlacement = WidgetPlacement
    placements: list[WidgetPlacement] = []
    append_placement = placements.append
    view_region = size.region
    null_spacing = NULL_SPACING
    null_offset = NULL_OFFSET

    for split_widget in split_widgets:
        split = split_widget.styles.split
        box_model = split_widget._get_box_model(
            size, viewport, Fraction(size.width), Fraction(size.height)
        )
        widget_width_fraction, widget_height_fraction, margin = box_model
        if split == "bottom":
            widget_height = int(widget_height_fraction) + margin.height
            view_region, split_region = view_region.split_horizontal(-widget_height)
        elif split == "top":
            widget_height = int(widget_height_fraction) + margin.height
            split_region, view_region = view_region.split_horizontal(widget_height)
        elif split == "left":
            widget_width = int(widget_width_fraction) + margin.width
            split_region, view_region = view_region.split_vertical(widget_width)
        elif split == "right":
            widget_width = int(widget_width_fraction) + margin.width
            view_region, split_region = view_region.split_vertical(-widget_width)
        else:
            raise AssertionError("invalid value for split edge")  # pragma: no-cover

        append_placement(
            _WidgetPlacement(
                split_region, null_offset, null_spacing, split_widget, 1, True, False
            )
        )

    return placements, view_region
