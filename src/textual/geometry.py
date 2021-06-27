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
    """A point defined by x and y coordinates."""

    x: int
    y: int

    @property
    def is_origin(self) -> bool:
        x, y = self
        return x == 0 and y == 0

    def __add__(self, other: object) -> Point:
        if isinstance(other, Point):
            _x, _y = self
            x, y = other
            return Point(_x + x, _y + y)
        raise NotImplemented

    def __sub__(self, other: object) -> Point:
        if isinstance(other, Point):
            _x, _y = self
            x, y = other
            return Point(_x - x, _y - y)
        raise NotImplemented


class Dimensions(NamedTuple):
    """An area defined by its width and height."""

    width: int
    height: int

    def __bool__(self) -> bool:
        return self.width * self.height != 0

    def contains(self, x: int, y: int) -> bool:
        """Check if a point is in the region.

        Args:
            x (int): X coordinate (column)
            y (int): Y coordinate (row)

        Returns:
            bool: True if the point is within the region.
        """
        width, height = self
        return width > x >= 0 and height > y >= 0

    def contains_point(self, point: tuple[int, int]) -> bool:
        """Check if a point is in the region.

        Args:
            point (tuple[int, int]): A tuple of x and y coordinates.

        Returns:
            bool: True if the point is within the region.
        """
        x, y = point
        width, height = self
        return width > x >= 0 and height > y >= 0

    def __contains__(self, other: Any) -> bool:
        try:
            x, y = other
        except Exception:
            raise TypeError(
                "Dimensions.__contains__ requires an iterable of two integers"
            )
        width, height = self
        return width > x >= 0 and height > y >= 0


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
        """Get the area within the region."""
        return self.width * self.height

    @property
    def origin(self) -> Point:
        """Get the start point of the region."""
        return Point(self.x, self.y)

    @property
    def limit(self) -> Point:
        x, y, width, height = self
        return Point(x + width, y + height)

    @property
    def limit_inclusive(self) -> Point:
        """Get the end point of the region."""
        x, y, width, height = self
        return Point(x + width - 1, y + height - 1)

    @property
    def size(self) -> Dimensions:
        """Get the size of the region."""
        return Dimensions(self.width, self.height)

    @property
    def extents(self) -> tuple[int, int, int, int]:
        """Get the maxima and minima of region.

        Returns:
            tuple[int, int, int, int]: A tuple of (<min x>, <max x>, <min y>, <max y>)
        """
        x, y, width, height = self
        return x, width + x, y, height + y

    def overlaps(self, other: Region) -> bool:
        """Check if another region overlaps this region.

        Args:
            other (Region): A Region.

        Returns:
            bool: True if other region shares any cells with this region.
        """
        x, x2, y, y2 = self.extents
        ox, ox2, oy, oy2 = other.extents

        return ((x2 > ox >= x) or (x2 > ox2 >= x) or (ox < x and ox2 > x2)) and (
            (y2 > oy >= y) or (y2 > oy2 >= y) or (oy < y and oy2 > x2)
        )

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
        """Check if a point is in the region.

        Args:
            point (tuple[int, int]): A tuple of x and y coordinates.

        Returns:
            bool: True if the point is within the region.
        """
        self_x, self_y, width, height = self
        x, y = point
        return ((self_x + width) > x >= self_x) and (((self_y + height) > y >= self_y))

    def translate(self, x: int, y: int) -> Region:
        """Move the origin of the Region.

        Args:
            x (int): x Coordinate.
            y (int): y Coordinate.

        Returns:
            Region: A new region shifted by x, y
        """

        _x, _y, width, height = self
        return Region(_x + x, _y + y, width, height)

    def __contains__(self, other: Any) -> bool:
        try:
            x, y = other
        except Exception:
            raise TypeError("Region.__contains__ requires an iterable of two integers")
        self_x, self_y, width, height = self
        return ((self_x + width) > x >= self_x) and (((self_y + height) > y >= self_y))
