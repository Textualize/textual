from __future__ import annotations

from typing import Callable, NamedTuple

from .geometry import Size, Spacing
from .css.styles import StylesBase


class BoxModel(NamedTuple):
    """The result of `get_box_model`."""

    size: Size  # Content + padding + border
    margin: Spacing  # Additional margin


def get_box_model(
    styles: StylesBase,
    container: Size,
    viewport: Size,
    get_content_width: Callable[[Size, Size], int],
    get_content_height: Callable[[Size, Size], int],
) -> BoxModel:
    """Resolve the box model for this Styles.

    Args:
        styles (StylesBase): Styles object.
        container (Size): The size of the widget container.
        viewport (Size): The viewport size.
        get_auto_width (Callable): A callable which accepts container size and parent size and returns a width.
        get_auto_height (Callable): A callable which accepts container size and parent size and returns a height.

    Returns:
        BoxModel: A tuple with the size of the content area and margin.
    """

    has_rule = styles.has_rule
    width, height = container
    is_content_box = styles.box_sizing == "content-box"
    gutter = styles.padding + styles.border.spacing

    if not has_rule("width"):
        width = container.width
    elif styles.width.is_auto:
        # When width is auto, we want enough space to always fit the content
        width = get_content_width(container, viewport)
        if not is_content_box:
            # If box sizing is border box we want to enlarge the width so that it
            # can accommodate padding + border
            width += gutter.width
    else:
        width = styles.width.resolve_dimension(container, viewport)

    if not has_rule("height"):
        height = container.height
    elif styles.height.is_auto:
        height = get_content_height(container, viewport)
        if not is_content_box:
            height += gutter.height
    else:
        height = styles.height.resolve_dimension(container, viewport)

    if is_content_box:
        gutter_width, gutter_height = gutter.totals
        width += gutter_width
        height += gutter_height

    if has_rule("min_width"):
        min_width = styles.min_width.resolve_dimension(container, viewport)
        width = max(width, min_width)

    if has_rule("max_width"):
        max_width = styles.max_width.resolve_dimension(container, viewport)
        width = min(width, max_width)

    if has_rule("min_height"):
        min_height = styles.min_height.resolve_dimension(container, viewport)
        height = max(height, min_height)

    if has_rule("max_height"):
        max_height = styles.max_height.resolve_dimension(container, viewport)
        height = min(height, max_height)

    size = Size(width, height)
    margin = styles.margin

    return BoxModel(size, margin)
