from __future__ import annotations

from fractions import Fraction
from itertools import accumulate
from typing import TYPE_CHECKING, Iterable, Sequence, cast

from typing_extensions import Literal

from .box_model import BoxModel
from .css.scalar import Scalar
from .css.styles import RenderStyles
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
        sum([scalar.value for scalar, fraction in resolved if fraction is None])
    )

    if total_fraction:
        total_gutter = gutter * (len(dimensions) - 1)
        consumed = sum([fraction for _, fraction in resolved if fraction is not None])
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


def resolve_fraction_unit(
    widget_styles: Iterable[RenderStyles],
    size: Size,
    viewport_size: Size,
    remaining_space: Fraction,
    resolve_dimension: Literal["width", "height"] = "width",
) -> Fraction:
    """Calculate the fraction.

    Args:
        widget_styles: Styles for widgets with fraction units.
        size: Container size.
        viewport_size: Viewport size.
        remaining_space: Remaining space for fr units.
        resolve_dimension: Which dimension to resolve.

    Returns:
        The value of 1fr.
    """
    if not remaining_space or not widget_styles:
        return Fraction(1)

    initial_space = remaining_space

    def resolve_scalar(
        scalar: Scalar | None, fraction_unit: Fraction = Fraction(1)
    ) -> Fraction | None:
        """Resolve a scalar if it is not None.

        Args:
            scalar: Optional scalar to resolve.
            fraction_unit: Size of 1fr.

        Returns:
            Fraction if resolved, otherwise None.
        """
        return (
            None
            if scalar is None
            else scalar.resolve(size, viewport_size, fraction_unit)
        )

    resolve: list[tuple[Scalar, Fraction | None, Fraction | None]] = []

    if resolve_dimension == "width":
        resolve = [
            (
                cast(Scalar, styles.width),
                resolve_scalar(styles.min_width),
                resolve_scalar(styles.max_width),
            )
            for styles in widget_styles
            if styles.overlay != "screen"
        ]
    else:
        resolve = [
            (
                cast(Scalar, styles.height),
                resolve_scalar(styles.min_height),
                resolve_scalar(styles.max_height),
            )
            for styles in widget_styles
            if styles.overlay != "screen"
        ]

    resolved: list[Fraction | None] = [None] * len(resolve)
    remaining_fraction = Fraction(sum(scalar.value for scalar, _, _ in resolve))

    while remaining_fraction > 0:
        remaining_space_changed = False
        resolve_fraction = Fraction(remaining_space, remaining_fraction)
        for index, (scalar, min_value, max_value) in enumerate(resolve):
            value = resolved[index]
            if value is None:
                resolved_scalar = scalar.resolve(size, viewport_size, resolve_fraction)
                if min_value is not None and resolved_scalar < min_value:
                    remaining_space -= min_value
                    remaining_fraction -= Fraction(scalar.value)
                    resolved[index] = min_value
                    remaining_space_changed = True
                elif max_value is not None and resolved_scalar > max_value:
                    remaining_space -= max_value
                    remaining_fraction -= Fraction(scalar.value)
                    resolved[index] = max_value
                    remaining_space_changed = True

        if not remaining_space_changed:
            break

    return (
        Fraction(remaining_space, remaining_fraction)
        if remaining_fraction > 0
        else initial_space
    )


def resolve_box_models(
    dimensions: list[Scalar | None],
    widgets: list[Widget],
    size: Size,
    viewport_size: Size,
    margin: Size,
    resolve_dimension: Literal["width", "height"] = "width",
) -> list[BoxModel]:
    """Resolve box models for a list of dimensions

    Args:
        dimensions: A list of Scalars or Nones for each dimension.
        widgets: Widgets in resolve.
        size: Size of container.
        viewport_size: Viewport size.
        margin: Total space occupied by margin
        resolve_dimension: Which dimension to resolve.

    Returns:
        List of resolved box models.
    """
    margin_width, margin_height = margin

    fraction_width = Fraction(max(0, size.width - margin_width))
    fraction_height = Fraction(max(0, size.height - margin_height))

    margin_size = size - margin

    # Fixed box models
    box_models: list[BoxModel | None] = [
        (
            None
            if _dimension is not None and _dimension.is_fraction
            else widget._get_box_model(
                size, viewport_size, fraction_width, fraction_height
            )
        )
        for (_dimension, widget) in zip(dimensions, widgets)
    ]

    if None not in box_models:
        # No fr units, so we're done
        return cast("list[BoxModel]", box_models)

    # If all box models have been calculated
    widget_styles = [widget.styles for widget in widgets]
    if resolve_dimension == "width":
        total_remaining = int(
            sum(
                [
                    box_model.width
                    for widget, box_model in zip(widgets, box_models)
                    if (box_model is not None and widget.styles.overlay != "screen")
                ]
            )
        )

        remaining_space = int(max(0, size.width - total_remaining - margin_width))
        fraction_unit = resolve_fraction_unit(
            [
                styles
                for styles in widget_styles
                if styles.width is not None
                and styles.width.is_fraction
                and styles.overlay != "screen"
            ],
            size,
            viewport_size,
            Fraction(remaining_space),
            resolve_dimension,
        )
        width_fraction = fraction_unit
        height_fraction = Fraction(margin_size.height)
    else:
        total_remaining = int(
            sum(
                [
                    box_model.height
                    for widget, box_model in zip(widgets, box_models)
                    if (box_model is not None and widget.styles.overlay != "screen")
                ]
            )
        )

        remaining_space = int(max(0, size.height - total_remaining - margin_height))
        fraction_unit = resolve_fraction_unit(
            [
                styles
                for styles in widget_styles
                if styles.height is not None
                and styles.height.is_fraction
                and styles.overlay != "screen"
            ],
            size,
            viewport_size,
            Fraction(remaining_space),
            resolve_dimension,
        )
        width_fraction = Fraction(margin_size.width)
        height_fraction = fraction_unit

    box_models = [
        box_model
        or widget._get_box_model(
            size,
            viewport_size,
            width_fraction,
            height_fraction,
        )
        for widget, box_model in zip(widgets, box_models)
    ]

    return cast("list[BoxModel]", box_models)
