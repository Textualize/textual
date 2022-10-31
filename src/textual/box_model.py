from __future__ import annotations

from fractions import Fraction
from typing import Callable, NamedTuple

from .css.styles import StylesBase
from .geometry import Size, Spacing


class BoxModel(NamedTuple):
    """The result of `get_box_model`."""

    # Content + padding + border
    width: Fraction
    height: Fraction
    margin: Spacing  # Additional margin


def get_box_model(
    styles: StylesBase,
    container: Size,
    viewport: Size,
    width_fraction: Fraction,
    height_fraction: Fraction,
    get_content_width: Callable[[Size, Size], int],
    get_content_height: Callable[[Size, Size, int], int],
) -> BoxModel:
    """Resolve the box model for this Styles.

    Args:
        styles (StylesBase): Styles object.
        container (Size): The size of the widget container.
        viewport (Size): The viewport size.
        width_fraction (Fraction): A fraction used for 1 `fr` unit on the width dimension.
        height_fraction (Fraction):A fraction used for 1 `fr` unit on the height dimension.
        get_auto_width (Callable): A callable which accepts container size and parent size and returns a width.
        get_auto_height (Callable): A callable which accepts container size and parent size and returns a height.

    Returns:
        BoxModel: A tuple with the size of the content area and margin.
    """
    _content_width, _content_height = container
    content_width = Fraction(_content_width)
    content_height = Fraction(_content_height)
    is_border_box = styles.box_sizing == "border-box"
    gutter = styles.gutter
    margin = styles.margin

    is_auto_width = styles.width and styles.width.is_auto
    is_auto_height = styles.height and styles.height.is_auto

    # Container minus padding and border
    content_container = container - gutter.totals
    # The container including the content
    sizing_container = content_container if is_border_box else container

    if styles.width is None:
        # No width specified, fill available space
        content_width = Fraction(content_container.width - margin.width)
    elif is_auto_width:
        # When width is auto, we want enough space to always fit the content
        content_width = Fraction(
            get_content_width(content_container - styles.margin.totals, viewport)
        )
    else:
        # An explicit width
        styles_width = styles.width
        content_width = styles_width.resolve_dimension(
            sizing_container - styles.margin.totals, viewport, width_fraction
        )
        if is_border_box and styles_width.excludes_border:
            content_width -= gutter.width

    if styles.min_width is not None:
        # Restrict to minimum width, if set
        min_width = styles.min_width.resolve_dimension(
            content_container, viewport, width_fraction
        )
        content_width = max(content_width, min_width)

    if styles.max_width is not None:
        # Restrict to maximum width, if set
        max_width = styles.max_width.resolve_dimension(
            content_container, viewport, width_fraction
        )
        if is_border_box:
            max_width -= gutter.width
        content_width = min(content_width, max_width)

    content_width = max(Fraction(0), content_width)

    if styles.height is None:
        # No height specified, fill the available space
        content_height = Fraction(content_container.height - margin.height)
    elif is_auto_height:
        # Calculate dimensions based on content
        content_height = Fraction(
            get_content_height(content_container, viewport, int(content_width))
        )
    else:
        styles_height = styles.height
        # Explicit height set
        content_height = styles_height.resolve_dimension(
            sizing_container - styles.margin.totals, viewport, height_fraction
        )
        if is_border_box and styles_height.excludes_border:
            content_height -= gutter.height

    if styles.min_height is not None:
        # Restrict to minimum height, if set
        min_height = styles.min_height.resolve_dimension(
            content_container, viewport, height_fraction
        )
        content_height = max(content_height, min_height)

    if styles.max_height is not None:
        # Restrict maximum height, if set
        max_height = styles.max_height.resolve_dimension(
            content_container, viewport, height_fraction
        )
        content_height = min(content_height, max_height)

    content_height = max(Fraction(1), content_height)
    model = BoxModel(
        content_width + gutter.width, content_height + gutter.height, margin
    )
    return model
