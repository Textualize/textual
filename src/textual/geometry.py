from __future__ import annotations

from typing import Any, NamedTuple, TypeVar, Iterable


T = TypeVar("T", int, float)


def clamp(value: T, minimum: T, maximum: T) -> T:
    """Clamp a value between two other values.

    Args:
        value (T): A value
        minimum (T): Minimum value
        maximum (T): maximum value

    Returns:
        T: New value that is not less than the minimum or greater than the maximum.
    """
    if minimum > maximum:
        maximum, minimum = minimum, maximum
    if value < minimum:
        return minimum
    elif value > maximum:
        return maximum
    else:
        return value


class Offset(NamedTuple):
    """A point defined by x and y coordinates."""

    x: int = 0
    y: int = 0

    @property
    def is_origin(self) -> bool:
        """Check if the point is at the origin (0, 0)."""
        return self == (0, 0)

    def __add__(self, other: object) -> Offset:
        if isinstance(other, tuple):
            _x, _y = self
            x, y = other
            return Offset(_x + x, _y + y)
        return NotImplemented

    def __sub__(self, other: object) -> Offset:
        if isinstance(other, tuple):
            _x, _y = self
            x, y = other
            return Offset(_x - x, _y - y)
        return NotImplemented

    def blend(self, destination: Offset, factor: float) -> Offset:
        """Blend (interpolate) to a new point.

        Args:
            destination (Offset): Offset where progress is 1.0
            factor (float): A value between 0 and 1.0

        Returns:
            Offset: A new point on a line between `self` and `destination`
        """
        x1, y1 = self
        x2, y2 = destination
        return Offset(int(x1 + (x2 - x1) * factor), int((y1 + (y2 - y1) * factor)))


class Size(NamedTuple):
    """An area defined by its width and height."""

    width: int
    height: int

    def __bool__(self) -> bool:
        """Return True if both width and height are nonzero."""
        return self.width * self.height != 0

    @property
    def area(self) -> int:
        """Get the area of the size.

        Returns:
            int: Area in cells.
        """
        return self.width * self.height

    @property
    def region(self) -> Region:
        """Get a region of the same size.
        
        Returns:
            Region: a `Region` instance of the same size, with origin (0, 0).
        """
        width, height = self
        return Region(0, 0, width, height)

    def contains(self, x: int, y: int) -> bool:
        """Check if a point is in the size.

        Args:
            x (int): X-coordinate (column)
            y (int): Y-coordinate (row)

        Returns:
            bool: True if the point is within the region.
        """
        width, height = self
        return width > x >= 0 and height > y >= 0

    def contains_point(self, point: tuple[int, int]) -> bool:
        """Check if a point is in the size.

        Args:
            point (tuple[int, int]): A tuple of x and y coordinates.

        Returns:
            bool: True if the point is within the region.
        """
        x, y = point
        width, height = self
        return width > x >= 0 and height > y >= 0

    def __contains__(self, other: Iterable[int]) -> bool:  # type: ignore[override]
        """Determine whether the dimensions of `other` are within the bounds of the size.
        
        Returns:
            bool: True if the dimensions of `other` are within the bounds of the size.
            
        Raises:
            TypeError if `other` cannot be unpacked into a two-item tuple.
        """
        # The signature of this method breaks LSP,
        # but it is useful to keep it as it is.

        try:
            x, y = other
        except Exception:
            raise TypeError(
                "Dimensions.__contains__ requires an iterable of two integers"
            )
        width, height = self
        return width > x >= 0 and height > y >= 0


R = TypeVar("R", bound="Region")


class Region(NamedTuple):
    """Defines a rectangular region."""

    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0

    @classmethod
    def from_corners(cls: type[R], x1: int, y1: int, x2: int, y2: int) -> R:
        """Construct a Region from the top-left and bottom-right corners.

        Args:
            x1 (int): Top-left x
            y1 (int): Top-left y
            x2 (int): Bottom-right x
            y2 (int): Bottom-right y

        Returns:
            Region: A new region.
        """
        return cls(x1, y1, x2 - x1, y2 - y1)

    @classmethod
    def from_origin(cls: type[R], origin: tuple[int, int], size: tuple[int, int]) -> R:
        """Create a new region from `origin` and `size`.

        Args:
            origin (tuple[int, int]): The origin (top-left point) of the new region.
            size (tuple[int, int]): The dimensions of the new region.

        Returns:
            Region: A new `Region` instance.
        """
        x, y = origin
        width, height = size
        return cls(x, y, width, height)

    def __bool__(self) -> bool:
        """Return True if the width and height of the region are both nonzero."""
        return bool(self.width and self.height)

    @property
    def x_extents(self) -> tuple[int, int]:
        """Get the starting and ending x-coordinates of the region.

        The end value is non-inclusive.

        Returns:
            tuple[int, int]: A tuple describing the minimum and maximum x-coordinates.
        """
        return (self.x, self.x + self.width)

    @property
    def y_extents(self) -> tuple[int, int]:
        """Get the starting and ending y-coordinates of the region.

        The end value is non-inclusive.

        Returns:
            tuple[int, int]: A tuple describing the minimum and maximum y-coordinates.
        """
        return (self.y, self.y + self.height)

    @property
    def x_max(self) -> int:
        """Get the ending x-coordinate.
        
        This value is non-inclusive.
        
        Returns:
            int: The x-coordinate.
        """
        return self.x + self.width

    @property
    def y_max(self) -> int:
        """Get the ending y-coordinate.
        
        This value is non-inclusive.
        
        Returns:
            int: The y-coordinate.
        """
        return self.y + self.height

    @property
    def area(self) -> int:
        """Get the area within the region.

        Returns:
            int: the size of the area.
        """
        return self.width * self.height

    @property
    def origin(self) -> Offset:
        """Get the start offset of the region.

        Returns:
            Offset: an (x, y) two-integer tuple.
        """
        return Offset(self.x, self.y)

    @property
    def size(self) -> Size:
        """Get the size of the region.
        
        Returns:
            Size: a (width, height) two-integer tuple.
        """
        return Size(self.width, self.height)

    @property
    def corners(self) -> tuple[int, int, int, int]:
        """Get the maxima and minima of the region.

        Returns:
            tuple[int, int, int, int]: A tuple of (<min x>, <min y>, <max x>, <max y>)
        """
        x, y, width, height = self
        return x, y, (x + width), (y + height)

    @property
    def x_range(self) -> range:
        """Get the range between the region's starting and ending x-coordinates.
        
        The end value is non-inclusive.
        
        Returns:
            range: a `range` instance with increment 1, from x-min to x-max.
        """
        return range(self.x, (self.x + self.width))

    @property
    def y_range(self) -> range:
        """Get the range between the region's starting and ending y-coordinates.
        
        The end value is non-inclusive.
        
        Returns:
            range: a `range` instance with increment 1, from y-min to y-max.
        """
        return range(self.y, (self.y + self.height))

    def __add__(self, other: Any) -> Region:
        if isinstance(other, tuple):
            ox, oy = other
            x, y, width, height = self
            return Region(x + ox, y + oy, width, height)
        return NotImplemented

    def __sub__(self, other: Any) -> Region:
        if isinstance(other, tuple):
            ox, oy = other
            x, y, width, height = self
            return Region(x - ox, y - oy, width, height)
        return NotImplemented

    def overlaps(self, other: Region) -> bool:
        """Check if another region overlaps this region.

        Args:
            other (Region): A Region.

        Returns:
            bool: True if the other region shares any cells with this region.
        """
        x, y, x2, y2 = self.corners
        ox, oy, ox2, oy2 = other.corners

        return ((x2 > ox >= x) or (x2 > ox2 > x) or (ox < x and ox2 >= x2)) and (
            (y2 > oy >= y) or (y2 > oy2 > y) or (oy < y and oy2 >= y2)
        )

    def contains(self, x: int, y: int) -> bool:
        """Check if an (x, y) point is in the region.

        Args:
            x (int): x-coordinate (column) of the point
            y (int): y-coordinate (row) of the point

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
            
        Raises:
            TypeError if `point` cannot be unpacked into a two-item tuple.
        """
        x1, y1, x2, y2 = self.corners
        try:
            ox, oy = point
        except Exception:
            raise TypeError(f"a tuple of two integers is required, not {point!r}")
        return (x2 > ox >= x1) and (y2 > oy >= y1)

    def contains_region(self, other: Region) -> bool:
        """Check if another region is entirely contained within this region.

        Args:
            other (Region): Another region.

        Returns:
            bool: True if the other region fits perfectly within this region.
        """
        x1, y1, x2, y2 = self.corners
        ox, oy, ox2, oy2 = other.corners
        return (x2 >= ox >= x1 and y2 >= oy >= y1) and (
            x2 >= ox2 >= x1 and y2 >= oy2 >= y1
        )

    def translate(self, x: int = 0, y: int = 0) -> Region:
        """Return a new region of the same size, with the origin shifted.

        Args:
            x (int): Value to add to x-coordinate for the new region. Optional; defaults to 0.
            y (int): Value to add to y-coordinate for the new region. Optional; defaults to 0.

        Returns:
            Region: A new `Region` instance of the same size, shifted by (x, y).
        """

        self_x, self_y, width, height = self
        return Region((self_x + x), (self_y + y), width, height)

    def __contains__(self, other: Any) -> bool:
        """Check if a point is in this region.
        
        The return value is always False unless `other`
        is either a `Region` instance or a tuple of two numbers.
        
        Returns:
            bool: True if `other` is contained in this region.
        """
        if isinstance(other, Region):
            return self.contains_region(other)
        else:
            try:
                return self.contains_point(other)
            except TypeError:
                return False

    def clip(self, width: int, height: int) -> Region:
        """Return a new region clipped within (width, height) bounds.

        Args:
            width (int): Width of the bounds.
            height (int): Height of the bounds.

        Returns:
            Region: A new `Region` instance clipped to fit within (width, height).
        """
        x1, y1, x2, y2 = self.corners

        # Save a local copy of `clamp` for optimisation
        _clamp = clamp
        new_region = Region.from_corners(
            _clamp(x1, 0, width),
            _clamp(y1, 0, height),
            _clamp(x2, 0, width),
            _clamp(y2, 0, height),
        )
        return new_region

    def intersection(self, region: Region) -> Region:
        """Find the overlap between two regions.

        The intersection, or overlap,
        is the area covered by both this region and the other.

        Args:
            region (Region): Another region that overlaps this region.

        Returns:
            Region: A new instance describing the intersection of this region and the other.
        """
        # Unrolled because this method is used a lot
        x1, y1, w1, h1 = self
        cx1, cy1, w2, h2 = region
        x2 = x1 + w1
        y2 = y1 + h1
        cx2 = cx1 + w2
        cy2 = cy1 + h2

        rx1 = cx2 if x1 > cx2 else (cx1 if x1 < cx1 else x1)
        ry1 = cy2 if y1 > cy2 else (cy1 if y1 < cy1 else y1)
        rx2 = cx2 if x2 > cx2 else (cx1 if x2 < cx1 else x2)
        ry2 = cy2 if y2 > cy2 else (cy1 if y2 < cy1 else y2)

        return Region(rx1, ry1, (rx2 - rx1), (ry2 - ry1))

    def union(self, region: Region) -> Region:
        """Return a new region containing this region and another.

        Args:
            region (Region): Another region.

        Returns:
            Region: A new instance describing a region containing both original regions.
        """
        x1, y1, x2, y2 = self.corners
        ox1, oy1, ox2, oy2 = region.corners

        union_region = Region.from_corners(
            min(x1, ox1), min(y1, oy1), max(x2, ox2), max(y2, oy2)
        )
        return union_region
