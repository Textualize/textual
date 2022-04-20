from __future__ import annotations


from typing import Callable, NamedTuple, TYPE_CHECKING

from .geometry import Size, Spacing
from .css.styles import StylesBase


class BoxModel(NamedTuple):
    content: Size
    margin: Spacing


def get_box_model(
    styles: StylesBase,
    container_size: Size,
    parent_size: Size,
    get_auto_width: Callable[[Size, Size], int],
    get_auto_height: Callable[[Size, Size], int],
) -> BoxModel:
    """Resolve the box model for this Styles.

    Args:
        styles (StylesBase): Styles object.
        container_size (Size): The size of the widget container.
        parent_size (Size): The size widget's parent.
        get_auto_width (Callable): A callable which accepts container size and parent size and returns a width.
        get_auto_height (Callable): A callable which accepts container size and parent size and returns a height.

    Returns:
        BoxModel: A tuple with the size of the content area and margin.
    """

    has_rule = styles.has_rule
    width, height = container_size

    extra = Size(0, 0)
    if styles.box_sizing == "content-box":
        if has_rule("padding"):
            extra += styles.padding.totals
        extra += styles.border.spacing.totals

    else:  # border-box
        extra -= styles.border.spacing.totals

    if has_rule("width"):
        if styles.width.is_auto:
            # extra_width = styles.padding.width + styles.border.spacing.width
            width = get_auto_width(container_size, parent_size)
        else:
            width = styles.width.resolve_dimension(container_size, parent_size)
    else:
        width = max(0, width - styles.margin.width)

    if styles.min_width:
        min_width = styles.min_width.resolve_dimension(container_size, parent_size)
        width = max(width, min_width)

    if styles.max_width:
        max_width = styles.max_width.resolve_dimension(container_size, parent_size)
        width = min(width, max_width)

    if has_rule("height"):
        if styles.height.is_auto:
            extra_height = styles.padding.height + styles.border.spacing.height
            height = get_auto_height(container_size, parent_size) + extra_height
        else:
            height = styles.height.resolve_dimension(container_size, parent_size)
    else:
        height = max(0, height - styles.margin.height)

    if styles.min_height:
        min_height = styles.min_height.resolve_dimension(container_size, parent_size)
        height = max(height, min_height)

    if styles.max_height:
        max_height = styles.max_height.resolve_dimension(container_size, parent_size)
        height = min(width, max_height)

    size = Size(width, height) + extra
    margin = styles.margin if has_rule("margin") else Spacing(0, 0, 0, 0)

    return BoxModel(size, margin)
