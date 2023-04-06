from __future__ import annotations

from fractions import Fraction
from typing import NamedTuple

from .geometry import Spacing


class BoxModel(NamedTuple):
    """The result of `get_box_model`."""

    # Content + padding + border
    width: Fraction
    height: Fraction
    margin: Spacing  # Additional margin
