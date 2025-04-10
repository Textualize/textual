from fractions import Fraction
from typing import NamedTuple


class Extrema(NamedTuple):
    """Specifies minimum and maximum dimensions."""

    min_width: Fraction | None = None
    max_width: Fraction | None = None
    min_height: Fraction | None = None
    max_height: Fraction | None = None

    def apply_width(self, width: Fraction) -> Fraction:
        """Apply width extrema.

        Args:
            width: Width value.

        Returns:
            Width, clamped between minimum and maximum.

        """
        min_width, max_width = self[:2]
        if min_width is not None:
            width = max(width, min_width)
        if max_width is not None:
            width = min(width, max_width)
        return width

    def apply_height(self, height: Fraction) -> Fraction:
        """Apply height extrema.

        Args:
            height: Height value.

        Returns:
            Height, clamped between minimum and maximum.

        """
        min_height, max_height = self[2:]
        if min_height is not None:
            height = max(height, min_height)
        if max_height is not None:
            height = min(height, max_height)
        return height
