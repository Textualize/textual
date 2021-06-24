from __future__ import annotations

from typing import Any, NamedTuple, TypeVar


T = TypeVar("T", int, float)


def clamp(value: T, minimum: T, maximum: T) -> T:
    """Clamps a value between two other values.

    Args:
        value (T): A value
        minimum (T): Minimum value
        maximum (T): maximum value

    Returns:
        T: New value that is not less than the minimum or greater than the maximum.
    """
    return min(max(value, minimum), maximum)


class Point(NamedTuple):
    x: int
    y: int

    def __add__(self, other: object) -> Point:
        if isinstance(other, Point):
            _x, _y = self
            x, y = other
            return Point(_x + x, _y + y)
        raise NotImplemented


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

    def translate(self, x: int, y: int) -> Region:
        _x, _y, width, height = self
        return Region(_x + x, _y + y, width, height)

    def __contains__(self, other: Any) -> bool:
        try:
            x, y = other
        except Exception:
            raise TypeError("Region.__contains__ requires an iterable of two integers")
        self_x, self_y, width, height = self
        return ((self_x + width) > x >= self_x) and (((self_y + height) > y >= self_y))
