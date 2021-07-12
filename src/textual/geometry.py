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
    if value < minimum:
        return minimum
    elif value > maximum:
        return maximum
    else:
        return value


class Point(NamedTuple):
    """A point defined by x and y coordinates."""

    x: int
    y: int

    @property
    def is_origin(self) -> bool:
        """Check if the point is at the origin (0, 0)"""
        return self == (0, 0)

    def __add__(self, other: object) -> Point:
        if isinstance(other, tuple):
            _x, _y = self
            x, y = other
            return Point(_x + x, _y + y)
        return NotImplemented

    def __sub__(self, other: object) -> Point:
        if isinstance(other, tuple):
            _x, _y = self
            x, y = other
            return Point(_x - x, _y - y)
        return NotImplemented

    def blend(self, destination: Point, factor: float) -> Point:
        """Blend (interpolate) to a new point.

        Args:
            destination (Point): Point where progress is 1.0
            factor (float): A value between 0 and 1.0

        Returns:
            Point: A new point on a line between self and destination
        """
        x1, y1 = self
        x2, y2 = destination
        return Point(int(x1 + (x2 - x1) * factor), int((y1 + (y2 - y1) * factor)))


class Dimensions(NamedTuple):
    """An area defined by its width and height."""

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

    @classmethod
    def from_corners(cls, x1: int, y1: int, x2: int, y2: int) -> Region:
        """Construct a Region form the top left and bottom right corners.

        Args:
            x1 (int): Top left x
            y1 (int): Top left y
            x2 (int): Bottom right x
            y2 (int): Bottom right y

        Returns:
            Region: A new region.
        """
        return cls(x1, y1, x2 - x1, y2 - y1)

    def __bool__(self) -> bool:
        return self.width != 0 and self.height != 0

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
    def corners(self) -> tuple[int, int, int, int]:
        """Get the maxima and minima of region.

        Returns:
            tuple[int, int, int, int]: A tuple of (<min x>, <max x>, <min y>, <max y>)
        """
        x, y, width, height = self
        return x, y, x + width, y + height

    def __add__(self, other: Any) -> Region:
        if isinstance(other, tuple):
            ox, oy = other
            x, y, width, height = self
            return Region(x + ox, y + oy, width, height)
        return NotImplemented

    def overlaps(self, other: Region) -> bool:
        """Check if another region overlaps this region.

        Args:
            other (Region): A Region.

        Returns:
            bool: True if other region shares any cells with this region.
        """
        x, y, x2, y2 = self.corners
        ox, oy, ox2, oy2 = other.corners

        return ((x2 > ox >= x) or (x2 > ox2 > x) or (ox < x and ox2 > x2)) and (
            (y2 > oy >= y) or (y2 > oy2 > y) or (oy < y and oy2 > y2)
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
        return (self_x + width > x >= self_x) and (self_y + height > y >= self_y)

    def contains_point(self, point: tuple[int, int]) -> bool:
        """Check if a point is in the region.

        Args:
            point (tuple[int, int]): A tuple of x and y coordinates.

        Returns:
            bool: True if the point is within the region.
        """
        x1, y1, x2, y2 = self.corners
        try:
            ox, oy = point
        except Exception:
            raise TypeError(f"a tuple of two integers is required, not {point!r}")
        return (x2 > ox >= x1) and (y2 > oy >= y1)

    def contains_region(self, other: Region) -> bool:
        """Check if a region is entirely contained within this region.

        Args:
            other (Region): A region.

        Returns:
            bool: True if the other region fits perfectly within this region.
        """
        x1, y1, x2, y2 = self.corners
        ox, oy, ox2, oy2 = other.corners
        return (x2 >= ox >= x1 and y2 >= oy >= y1) and (
            x2 >= ox2 >= x1 and y2 >= oy2 >= y1
        )

    def translate(self, translate_x: int, translate_y: int) -> Region:
        """Move the origin of the Region.

        Args:
            translate_x (int): Value to add to x coordinate.
            translate_y (int): Value to add to y coordinate.

        Returns:
            Region: A new region shifted by x, y
        """

        x, y, width, height = self
        return Region(x + translate_x, y + translate_y, width, height)

    def __contains__(self, other: Any) -> bool:
        """Check if a point is in this region."""
        if isinstance(other, Region):
            return self.contains_region(other)
        else:
            try:
                return self.contains_point(other)
            except TypeError:
                return False

    def clip(self, width: int, height: int) -> Region:
        """Clip this region to fit within width, height.

        Args:
            width (int): Width of bounds.
            height (int): Height of bounds.

        Returns:
            Region: Clipped region.
        """
        x1, y1, x2, y2 = self.corners

        new_region = Region.from_corners(
            clamp(x1, 0, width),
            clamp(y1, 0, height),
            clamp(x2, 0, width),
            clamp(y2, 0, height),
        )
        return new_region

    def clip_region(self, region: Region) -> Region:
        """Clip this region to fit within another region.

        Args:
            region ([type]): A region that overlaps this region.

        Returns:
            Region: A new region that fits within ``region``.
        """
        x1, y1, x2, y2 = self.corners
        cx1, cy1, cx2, cy2 = region.corners

        new_region = Region.from_corners(
            clamp(x1, cx1, cx2),
            clamp(y1, cy1, cy2),
            clamp(x2, cx2, cx2),
            clamp(y2, cy2, cy2),
        )
        return new_region


if __name__ == "__main__":
    from rich import print

    region = Region(-5, -5, 60, 100)

    print(region.clip(80, 25))

    region = Region(10, 10, 90, 90)

    print(region.corners)

    print((15, 15) in region)
    print((5, 15) in region)
    print(Region(15, 15, 10, 10) in region)
