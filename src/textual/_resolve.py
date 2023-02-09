from __future__ import annotations

from fractions import Fraction
from itertools import accumulate
from typing import TYPE_CHECKING, Sequence, cast

from typing_extensions import Literal

from .box_model import BoxModel
from .css.scalar import Scalar
from .geometry import Size

if TYPE_CHECKING:
    from .widget import Widget


def resolve(
    dimensions: Sequence[Scalar],
    total: int,
    gutter: int,
    size: Size,
    viewport: Size,
) -> list[tuple[int, int]]:
    """Resolve a list of dimensions.

    Args:
        dimensions: Scalars for column / row sizes.
        total: Total space to divide.
        gutter: Gutter between rows / columns.
        size: Size of container.
        viewport: Size of viewport.

    Returns:
        List of (<OFFSET>, <LENGTH>)
    """

    resolved: list[tuple[Scalar, Fraction | None]] = [
        (
            (scalar, None)
            if scalar.is_fraction
            else (scalar, scalar.resolve(size, viewport))
        )
        for scalar in dimensions
    ]

    from_float = Fraction.from_float
    total_fraction = from_float(
        sum(scalar.value for scalar, fraction in resolved if fraction is None)
    )

    if total_fraction:
        total_gutter = gutter * (len(dimensions) - 1)
        consumed = sum(fraction for _, fraction in resolved if fraction is not None)
        remaining = max(Fraction(0), Fraction(total - total_gutter) - consumed)
        fraction_unit = Fraction(remaining, total_fraction)
        resolved_fractions = [
            from_float(scalar.value) * fraction_unit if fraction is None else fraction
            for scalar, fraction in resolved
        ]
    else:
        resolved_fractions = cast(
            "list[Fraction]", [fraction for _, fraction in resolved]
        )

    fraction_gutter = Fraction(gutter)
    offsets = [0] + [
        int(fraction)
        for fraction in accumulate(
            value
            for fraction in resolved_fractions
            for value in (fraction, fraction_gutter)
        )
    ]
    results = [
        (offset1, offset2 - offset1)
        for offset1, offset2 in zip(offsets[::2], offsets[1::2])
    ]

    return results


def resolve_box_models(
    dimensions: list[Scalar | None],
    widgets: list[Widget],
    size: Size,
    parent_size: Size,
    dimension: Literal["width", "height"] = "width",
) -> list[BoxModel]:
    """Resolve box models for a list of dimensions

    Args:
        dimensions: A list of Scalars or Nones for each dimension.
        widgets: Widgets in resolve.
        size: Size of container.
        parent_size: Size of parent.
        dimensions: Which dimension to resolve.

    Returns:
        List of resolved box models.
    """

    fraction_width = Fraction(size.width)
    fraction_height = Fraction(size.height)
    box_models: list[BoxModel | None] = [
        (
            None
            if dimension is not None and dimension.is_fraction
            else widget._get_box_model(
                size, parent_size, fraction_width, fraction_height
            )
        )
        for (dimension, widget) in zip(dimensions, widgets)
    ]

    if dimension == "width":
        total_remaining = sum(
            box_model.width for box_model in box_models if box_model is not None
        )
        remaining_space = max(0, size.width - total_remaining)
    else:
        total_remaining = sum(
            box_model.height for box_model in box_models if box_model is not None
        )
        remaining_space = max(0, size.height - total_remaining)

    fraction_unit = Fraction(
        remaining_space,
        int(
            sum(
                dimension.value
                for dimension in dimensions
                if dimension and dimension.is_fraction
            )
        )
        or 1,
    )
    if dimension == "width":
        width_fraction = fraction_unit
        height_fraction = Fraction(size.height)
    else:
        width_fraction = Fraction(size.width)
        height_fraction = fraction_unit

    box_models = [
        box_model
        or widget._get_box_model(
            size,
            parent_size,
            width_fraction,
            height_fraction,
        )
        for widget, box_model in zip(widgets, box_models)
    ]

    return cast("list[BoxModel]", box_models)
