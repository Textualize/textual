from __future__ import annotations

from fractions import Fraction
from itertools import accumulate
from typing import cast, Sequence

from .css.scalar import Scalar
from .geometry import Size


def resolve(
    dimensions: Sequence[Scalar],
    total: int,
    gutter: int,
    size: Size,
    viewport: Size,
) -> list[tuple[int, int]]:
    """Resolve a list of dimensions.

    Args:
        dimensions (Sequence[Scalar]): Scalars for column / row sizes.
        total (int): Total space to divide.
        gutter (int): Gutter between rows / columns.
        size (Size): Size of container.
        viewport (Size): Size of viewport.

    Returns:
        list[tuple[int, int]]: List of (<OFFSET>, <LENGTH>)
    """

    resolved: list[tuple[Scalar, Fraction | None]] = [
        (
            (scalar, None)
            if scalar.is_fraction
            else (scalar, scalar.resolve_dimension(size, viewport))
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
