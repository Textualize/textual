"""

Functions and classes to manage terminal geometry (anything involving coordinates or dimensions).

"""


from __future__ import annotations

from math import sqrt
from typing import Any, cast, NamedTuple, Tuple, Union, TypeVar


SpacingDimensions = Union[int, Tuple[int], Tuple[int, int], Tuple[int, int, int, int]]


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
        """Check if the point is at the origin (0, 0)"""
        return self == (0, 0)

    def __bool__(self) -> bool:
        return self != (0, 0)

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

    def __mul__(self, other: object) -> Offset:
        if isinstance(other, (float, int)):
            x, y = self
            return Offset(int(x * other), int(y * other))
        return NotImplemented

    def blend(self, destination: Offset, factor: float) -> Offset:
        """Blend (interpolate) to a new point.

        Args:
            destination (Point): Point where progress is 1.0
            factor (float): A value between 0 and 1.0

        Returns:
            Point: A new point on a line between self and destination
        """
        x1, y1 = self
        x2, y2 = destination
        return Offset(int(x1 + (x2 - x1) * factor), int((y1 + (y2 - y1) * factor)))

    def get_distance_to(self, other: Offset) -> float:
        """Get the distance to another offset.

        Args:
            other (Offset): An offset

        Returns:
            float: Distance to other offset
        """
        x1, y1 = self
        x2, y2 = other
        distance = sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))
        return distance


class Size(NamedTuple):
    """An area defined by its width and height."""

    width: int = 0
    height: int = 0

    def __bool__(self) -> bool:
        """A Size is Falsy if it has area 0."""
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
        """Get a region of the same size."""
        width, height = self
        return Region(0, 0, width, height)

    def __add__(self, other: object) -> Size:
        if isinstance(other, Spacing):
            width, height = self
            other_width, other_height = other.totals
            return Size(width + other_width, height + other_height)

        if isinstance(other, tuple):
            width, height = self
            width2, height2 = other
            return Size(max(0, width + width2), max(0, height + height2))
        return NotImplemented

    def __sub__(self, other: object) -> Size:
        if isinstance(other, tuple):
            width, height = self
            width2, height2 = other
            return Size(max(0, width - width2), max(0, height - height2))
        return NotImplemented

    def contains(self, x: int, y: int) -> bool:
        """Check if a point is in the size.

        Args:
            x (int): X coordinate (column)
            y (int): Y coordinate (row)

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
    """Defines a rectangular region."""

    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0

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

    @classmethod
    def from_origin(cls, origin: tuple[int, int], size: tuple[int, int]) -> Region:
        """Create a region from origin and size.

        Args:
            origin (Point): Origin (top left point)
            size (tuple[int, int]): Dimensions of region.

        Returns:
            Region: A region instance.
        """
        x, y = origin
        width, height = size
        return cls(x, y, width, height)

    def __bool__(self) -> bool:
        """A Region is considered False when it has no area."""
        return bool(self.width and self.height)

    @property
    def x_extents(self) -> tuple[int, int]:
        """Get the starting and ending x coord.

        The end value is non inclusive.

        Returns:
            tuple[int, int]: [description]
        """
        return (self.x, self.x + self.width)

    @property
    def y_extents(self) -> tuple[int, int]:
        """Get the starting and ending x coord.

        The end value is non inclusive.

        Returns:
            tuple[int, int]: [description]
        """
        return (self.y, self.y + self.height)

    @property
    def x_max(self) -> int:
        """Maximum X value (non inclusive)"""
        return self.x + self.width

    @property
    def y_max(self) -> int:
        """Maximum Y value (non inclusive)"""
        return self.y + self.height

    @property
    def area(self) -> int:
        """Get the area within the region."""
        return self.width * self.height

    @property
    def origin(self) -> Offset:
        """Get the start point of the region."""
        return Offset(self.x, self.y)

    @property
    def size(self) -> Size:
        """Get the size of the region."""
        return Size(self.width, self.height)

    @property
    def corners(self) -> tuple[int, int, int, int]:
        """Get the maxima and minima of region.

        Returns:
            tuple[int, int, int, int]: A tuple of (<min x>, <max x>, <min y>, <max y>)
        """
        x, y, width, height = self
        return x, y, x + width, y + height

    @property
    def x_range(self) -> range:
        """A range object for X coordinates"""
        return range(self.x, self.x + self.width)

    @property
    def y_range(self) -> range:
        """A range object for Y coordinates"""
        return range(self.y, self.y + self.height)

    def __add__(self, other: object) -> Region:
        if isinstance(other, tuple):
            ox, oy = other
            x, y, width, height = self
            return Region(x + ox, y + oy, width, height)
        return NotImplemented

    def __sub__(self, other: object) -> Region:
        if isinstance(other, tuple):
            ox, oy = other
            x, y, width, height = self
            return Region(x - ox, y - oy, width, height)
        return NotImplemented

    def expand(self, size: tuple[int, int]) -> Region:
        """Increase the size of the region by adding a border.

        Args:
            size (tuple[int, int]): Additional width and height.

        Returns:
            Region: A new region.
        """
        expand_width, expand_height = size
        x, y, width, height = self
        return Region(
            x - expand_width,
            y - expand_height,
            width + expand_width * 2,
            height + expand_height * 2,
        )

    def overlaps(self, other: Region) -> bool:
        """Check if another region overlaps this region.

        Args:
            other (Region): A Region.

        Returns:
            bool: True if other region shares any cells with this region.
        """
        x, y, x2, y2 = self.corners
        ox, oy, ox2, oy2 = other.corners

        return ((x2 > ox >= x) or (x2 > ox2 > x) or (ox < x and ox2 >= x2)) and (
            (y2 > oy >= y) or (y2 > oy2 > y) or (oy < y and oy2 >= y2)
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

    def translate(self, x: int = 0, y: int = 0) -> Region:
        """Move the origin of the Region.

        Args:
            translate_x (int): Value to add to x coordinate.
            translate_y (int): Value to add to y coordinate.

        Returns:
            Region: A new region shifted by x, y
        """

        self_x, self_y, width, height = self
        return Region(self_x + x, self_y + y, width, height)

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

        _clamp = clamp
        new_region = Region.from_corners(
            _clamp(x1, 0, width),
            _clamp(y1, 0, height),
            _clamp(x2, 0, width),
            _clamp(y2, 0, height),
        )
        return new_region

    def shrink(self, margin: Spacing) -> Region:
        """Shrink a region by pushing each edge inwards.

        Args:
            margin (Spacing): Defines how many cells to shrink the Region by at each edge.

        Returns:
            Region: The new, smaller region.
        """
        _clamp = clamp
        top, right, bottom, left = margin
        x, y, width, height = self
        return Region(
            x=_clamp(x + left, 0, width),
            y=_clamp(y + top, 0, height),
            width=_clamp(width - left - right, 0, width),
            height=_clamp(height - top - bottom, 0, height),
        )

    def intersection(self, region: Region) -> Region:
        """Get that covers both regions.

        Args:
            region (Region): A region that overlaps this region.

        Returns:
            Region: A new region that fits within ``region``.
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

        return Region(rx1, ry1, rx2 - rx1, ry2 - ry1)

    def union(self, region: Region) -> Region:
        """Get a new region that contains both regions.

        Args:
            region (Region): [description]

        Returns:
            Region: [description]
        """
        x1, y1, x2, y2 = self.corners
        ox1, oy1, ox2, oy2 = region.corners

        union_region = self.from_corners(
            min(x1, ox1), min(y1, oy1), max(x2, ox2), max(y2, oy2)
        )
        return union_region

    def split(self, cut_x: int, cut_y: int) -> tuple[Region, Region, Region, Region]:
        """Split a region in to 4 from given x and y offsets (cuts).

                   cut_x ↓
                ┌────────┐┌───┐
                │        ││   │
                │        ││   │
                │        ││   │
        cut_y → └────────┘└───┘
                ┌────────┐┌───┐
                │        ││   │
                └────────┘└───┘

        Args:
            cut_x (int): Offset from self.x where the cut should be made. If negative, the cut
                is taken from the right edge.
            cut_y (int): Offset from self.y where the cut should be made. If negative, the cut
                is taken from the lower edge.

        Returns:
            tuple[Region, Region, Region, Region]: Four new regions which add up to the original (self).
        """

        x, y, width, height = self
        if cut_x < 0:
            cut_x = width + cut_x
        if cut_y < 0:
            cut_y = height + cut_y

        _Region = Region
        return (
            _Region(x, y, cut_x, cut_y),
            _Region(x + cut_x, y, width - cut_x, cut_y),
            _Region(x, y + cut_y, cut_x, height - cut_y),
            _Region(x + cut_x, y + cut_y, width - cut_x, height - cut_y),
        )

    def split_vertical(self, cut: int) -> tuple[Region, Region]:
        """Split a region in to two, from a given x offset.

                 cut ↓
            ┌────────┐┌───┐
            │        ││   │
            │        ││   │
            └────────┘└───┘

        Args:
            cut (int): An offset from self.x where the cut should be made. If cut is negative,
                it is taken from the right edge.

        Returns:
            tuple[Region, Region]: Two regions, which add up to the original (self).
        """

        x, y, width, height = self
        if cut < 0:
            cut = width + cut

        return (
            Region(x, y, cut, height),
            Region(x + cut, y, width - cut, height),
        )

    def split_horizontal(self, cut: int) -> tuple[Region, Region]:
        """Split a region in to two, from a given x offset.

                    ┌─────────┐
                    │         │
                    │         │
            cut →   └─────────┘
                    ┌─────────┐
                    └─────────┘

        Args:
            cut (int): An offset from self.x where the cut should be made. May be negative,
                for the offset to start from the right edge.

        Returns:
            tuple[Region, Region]: Two regions, which add up to the original (self).
        """
        x, y, width, height = self
        if cut < 0:
            cut = height + cut

        return (
            Region(x, y, width, cut),
            Region(x, y + cut, width, height - cut),
        )


class Spacing(NamedTuple):
    """The spacing around a renderable."""

    top: int = 0
    right: int = 0
    bottom: int = 0
    left: int = 0

    def __bool__(self) -> bool:
        return self != (0, 0, 0, 0)

    @property
    def width(self) -> int:
        """Total space in width."""
        return self.left + self.right

    @property
    def height(self) -> int:
        """Total space in height."""
        return self.top + self.bottom

    @property
    def top_left(self) -> tuple[int, int]:
        """Top left space."""
        return (self.left, self.top)

    @property
    def bottom_right(self) -> tuple[int, int]:
        """Bottom right space."""
        return (self.right, self.bottom)

    @property
    def totals(self) -> tuple[int, int]:
        top, right, bottom, left = self
        return (left + right, top + bottom)

    @property
    def css(self) -> str:
        """Gets a string containing the spacing in CSS format."""
        top, right, bottom, left = self
        if top == right == bottom == left:
            return f"{top}"
        if (top, right) == (bottom, left):
            return f"{top} {right}"
        else:
            return f"{top} {right} {bottom} {left}"

    @classmethod
    def unpack(cls, pad: SpacingDimensions) -> Spacing:
        """Unpack padding specified in CSS style."""
        if isinstance(pad, int):
            return cls(pad, pad, pad, pad)
        pad_len = len(pad)
        if pad_len == 1:
            _pad = pad[0]
            return cls(_pad, _pad, _pad, _pad)
        if pad_len == 2:
            pad_top, pad_right = cast(Tuple[int, int], pad)
            return cls(pad_top, pad_right, pad_top, pad_right)
        if pad_len == 4:
            top, right, bottom, left = cast(Tuple[int, int, int, int], pad)
            return cls(top, right, bottom, left)
        raise ValueError(f"1, 2 or 4 integers required for spacing; {pad_len} given")

    def __add__(self, other: object) -> Spacing:
        if isinstance(other, tuple):
            top1, right1, bottom1, left1 = self
            top2, right2, bottom2, left2 = other
            return Spacing(
                top1 + top2, right1 + right2, bottom1 + bottom2, left1 + left2
            )
        return NotImplemented


NULL_OFFSET = Offset(0, 0)
