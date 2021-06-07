from __future__ import annotations

from typing import Any, NamedTuple


class Point(NamedTuple):
    x: int
    y: int


class Dimensions(NamedTuple):
    width: int
    height: int

    def __bool__(self) -> bool:
        return self.width * self.height != 0


class Region(NamedTuple):
    """Defines a rectangular region of the screen."""

    x: int
    y: int
    width: int
    height: int

    def __bool__(self) -> bool:
        return self.width * self.height != 0

    @property
    def area(self) -> int:
        return self.width * self.height

    def contains(self, x: int, y: int) -> bool:
        """Check if a point is in the region.

        Args:
            x (int): X coordinate (column)
            y (int): Y coordinate (row)

        Returns:
            bool: True if the point is within the region.
        """
        self_x, self_y, width, height = self
        return ((self_x + width) > x >= self_x) and (((self_y + height) > y >= self_y))

    def contains_point(self, point: tuple[int, int]) -> bool:
        self_x, self_y, width, height = self
        x, y = point
        return ((self_x + width) > x >= self_x) and (((self_y + height) > y >= self_y))

    def __contains__(self, other: Any) -> bool:
        try:
            x, y = other
        except Exception:
            raise TypeError("Region.__contains__ requires an iterable of two integers")
        self_x, self_y, width, height = self
        return ((self_x + width) > x >= self_x) and (((self_y + height) > y >= self_y))
