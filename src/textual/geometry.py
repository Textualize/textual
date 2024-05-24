"""

Functions and classes to manage terminal geometry (anything involving coordinates or dimensions).
"""

from __future__ import annotations

from functools import lru_cache
from operator import attrgetter, itemgetter
from typing import (
    TYPE_CHECKING,
    Any,
    Collection,
    NamedTuple,
    Tuple,
    TypeVar,
    Union,
    cast,
)

from typing_extensions import Final

if TYPE_CHECKING:
    from typing_extensions import TypeAlias


SpacingDimensions: TypeAlias = Union[
    int, Tuple[int], Tuple[int, int], Tuple[int, int, int, int]
]
"""The valid ways in which you can specify spacing."""

T = TypeVar("T", int, float)


def clamp(value: T, minimum: T, maximum: T) -> T:
    """Adjust a value so it is not less than a minimum and not greater
    than a maximum value.

    Args:
        value: A value.
        minimum: Minimum value.
        maximum: Maximum value.

    Returns:
        New value that is not less than the minimum or greater than the maximum.
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
    """A cell offset defined by x and y coordinates.

    Offsets are typically relative to the top left of the terminal or other container.

    Textual prefers the names `x` and `y`, but you could consider `x` to be the _column_ and `y` to be the _row_.

    Offsets support addition, subtraction, multiplication, and negation.

    Example:
        ```python
        >>> from textual.geometry import Offset
        >>> offset = Offset(3, 2)
        >>> offset
        Offset(x=3, y=2)
        >>> offset += Offset(10, 0)
        >>> offset
        Offset(x=13, y=2)
        >>> -offset
        Offset(x=-13, y=-2)
        ```
    """

    x: int = 0
    """Offset in the x-axis (horizontal)"""
    y: int = 0
    """Offset in the y-axis (vertical)"""

    @property
    def is_origin(self) -> bool:
        """Is the offset at (0, 0)?"""
        return self == (0, 0)

    @property
    def clamped(self) -> Offset:
        """This offset with `x` and `y` restricted to values above zero."""
        x, y = self
        return Offset(0 if x < 0 else x, 0 if y < 0 else y)

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

    def __neg__(self) -> Offset:
        x, y = self
        return Offset(-x, -y)

    def blend(self, destination: Offset, factor: float) -> Offset:
        """Calculate a new offset on a line between this offset and a destination offset.

        Args:
            destination: Point where factor would be 1.0.
            factor: A value between 0 and 1.0.

        Returns:
            A new point on a line between self and destination.
        """
        x1, y1 = self
        x2, y2 = destination
        return Offset(
            int(x1 + (x2 - x1) * factor),
            int(y1 + (y2 - y1) * factor),
        )

    def get_distance_to(self, other: Offset) -> float:
        """Get the distance to another offset.

        Args:
            other: An offset.

        Returns:
            Distance to other offset.
        """
        x1, y1 = self
        x2, y2 = other
        distance: float = ((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)) ** 0.5
        return distance

    def clamp(self, width: int, height: int) -> Offset:
        """Clamp the offset to fit within a rectangle of width x height.

        Args:
            width: Width to clamp.
            height: Height to clamp.

        Returns:
            A new offset.
        """
        x, y = self
        return Offset(clamp(x, 0, width - 1), clamp(y, 0, height - 1))


class Size(NamedTuple):
    """The dimensions (width and height) of a rectangular region.

    Example:
        ```python
        >>> from textual.geometry import Size
        >>> size = Size(2, 3)
        >>> size
        Size(width=2, height=3)
        >>> size.area
        6
        >>> size + Size(10, 20)
        Size(width=12, height=23)
        ```
    """

    width: int = 0
    """The width in cells."""

    height: int = 0
    """The height in cells."""

    def __bool__(self) -> bool:
        """A Size is Falsy if it has area 0."""
        return self.width * self.height != 0

    @property
    def area(self) -> int:
        """The area occupied by a region of this size."""
        return self.width * self.height

    @property
    def region(self) -> Region:
        """A region of the same size, at the origin."""
        width, height = self
        return Region(0, 0, width, height)

    @property
    def line_range(self) -> range:
        """A range object that covers values between 0 and `height`."""
        return range(self.height)

    def with_width(self, width: int) -> Size:
        """Get a new Size with just the width changed.

        Args:
            width: New width.

        Returns:
            New Size instance.
        """
        return Size(width, self.height)

    def with_height(self, height: int) -> Size:
        """Get a new Size with just the height changed.

        Args:
            width: New height.

        Returns:
            New Size instance.
        """
        return Size(self.width, height)

    def __add__(self, other: object) -> Size:
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
        """Check if a point is in area defined by the size.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Returns:
            True if the point is within the region.
        """
        width, height = self
        return width > x >= 0 and height > y >= 0

    def contains_point(self, point: tuple[int, int]) -> bool:
        """Check if a point is in the area defined by the size.

        Args:
            point: A tuple of x and y coordinates.

        Returns:
            True if the point is within the region.
        """
        x, y = point
        width, height = self
        return width > x >= 0 and height > y >= 0

    def __contains__(self, other: Any) -> bool:
        try:
            x: int
            y: int
            x, y = other
        except Exception:
            raise TypeError(
                "Dimensions.__contains__ requires an iterable of two integers"
            )
        width, height = self
        return width > x >= 0 and height > y >= 0

    def clamp_offset(self, offset: Offset) -> Offset:
        """Clamp an offset to fit within the width x height.

        Args:
            offset: An offset.

        Returns:
            A new offset that will fit inside the dimensions defined in the Size.
        """
        return offset.clamp(self.width, self.height)


class Region(NamedTuple):
    """Defines a rectangular region.

    A Region consists of a coordinate (x and y) and dimensions (width and height).

    ```
      (x, y)
        ┌────────────────────┐ ▲
        │                    │ │
        │                    │ │
        │                    │ height
        │                    │ │
        │                    │ │
        └────────────────────┘ ▼
        ◀─────── width ──────▶
    ```

    Example:
        ```python
        >>> from textual.geometry import Region
        >>> region = Region(4, 5, 20, 10)
        >>> region
        Region(x=4, y=5, width=20, height=10)
        >>> region.area
        200
        >>> region.size
        Size(width=20, height=10)
        >>> region.offset
        Offset(x=4, y=5)
        >>> region.contains(1, 2)
        False
        >>> region.contains(10, 8)
        True
        ```
    """

    x: int = 0
    """Offset in the x-axis (horizontal)."""
    y: int = 0
    """Offset in the y-axis (vertical)."""
    width: int = 0
    """The width of the region."""
    height: int = 0
    """The height of the region."""

    @classmethod
    def from_union(cls, regions: Collection[Region]) -> Region:
        """Create a Region from the union of other regions.

        Args:
            regions: One or more regions.

        Returns:
            A Region that encloses all other regions.
        """
        if not regions:
            raise ValueError("At least one region expected")
        min_x = min(regions, key=itemgetter(0)).x
        max_x = max(regions, key=attrgetter("right")).right
        min_y = min(regions, key=itemgetter(1)).y
        max_y = max(regions, key=attrgetter("bottom")).bottom
        return cls(min_x, min_y, max_x - min_x, max_y - min_y)

    @classmethod
    def from_corners(cls, x1: int, y1: int, x2: int, y2: int) -> Region:
        """Construct a Region form the top left and bottom right corners.

        Args:
            x1: Top left x.
            y1: Top left y.
            x2: Bottom right x.
            y2: Bottom right y.

        Returns:
            A new region.
        """
        return cls(x1, y1, x2 - x1, y2 - y1)

    @classmethod
    def from_offset(cls, offset: tuple[int, int], size: tuple[int, int]) -> Region:
        """Create a region from offset and size.

        Args:
            offset: Offset (top left point).
            size: Dimensions of region.

        Returns:
            A region instance.
        """
        x, y = offset
        width, height = size
        return cls(x, y, width, height)

    @classmethod
    def get_scroll_to_visible(
        cls, window_region: Region, region: Region, *, top: bool = False
    ) -> Offset:
        """Calculate the smallest offset required to translate a window so that it contains
        another region.

        This method is used to calculate the required offset to scroll something in to view.

        Args:
            window_region: The window region.
            region: The region to move inside the window.
            top: Get offset to top of window.

        Returns:
            An offset required to add to region to move it inside window_region.
        """

        if region in window_region and not top:
            # Region is already inside the window, so no need to move it.
            return NULL_OFFSET

        window_left, window_top, window_right, window_bottom = window_region.corners
        region = region.crop_size(window_region.size)
        left, top_, right, bottom = region.corners
        delta_x = delta_y = 0

        if not (
            (window_right > left >= window_left)
            and (window_right > right >= window_left)
        ):
            # The region does not fit
            # The window needs to scroll on the X axis to bring region in to view
            delta_x = min(
                left - window_left,
                left - (window_right - region.width),
                key=abs,
            )

        if top:
            delta_y = top_ - window_top

        elif not (
            (window_bottom > top_ >= window_top)
            and (window_bottom > bottom >= window_top)
        ):
            # The window needs to scroll on the Y axis to bring region in to view
            delta_y = min(
                top_ - window_top,
                top_ - (window_bottom - region.height),
                key=abs,
            )
        return Offset(delta_x, delta_y)

    def __bool__(self) -> bool:
        """A Region is considered False when it has no area."""
        _, _, width, height = self
        return width * height > 0

    @property
    def column_span(self) -> tuple[int, int]:
        """A pair of integers for the start and end columns (x coordinates) in this region.

        The end value is *exclusive*.
        """
        return (self.x, self.x + self.width)

    @property
    def line_span(self) -> tuple[int, int]:
        """A pair of integers for the start and end lines (y coordinates) in this region.

        The end value is *exclusive*.
        """
        return (self.y, self.y + self.height)

    @property
    def right(self) -> int:
        """Maximum X value (non inclusive)."""
        return self.x + self.width

    @property
    def bottom(self) -> int:
        """Maximum Y value (non inclusive)."""
        return self.y + self.height

    @property
    def area(self) -> int:
        """The area under the region."""
        return self.width * self.height

    @property
    def offset(self) -> Offset:
        """The top left corner of the region.

        Returns:
            An offset.
        """
        return Offset(*self[:2])

    @property
    def center(self) -> tuple[float, float]:
        """The center of the region.

        Note, that this does *not* return an `Offset`, because the center may not be an integer coordinate.

        Returns:
            Tuple of floats.
        """
        x, y, width, height = self
        return (x + width / 2.0, y + height / 2.0)

    @property
    def bottom_left(self) -> Offset:
        """Bottom left offset of the region.

        Returns:
            An offset.
        """
        x, y, _width, height = self
        return Offset(x, y + height)

    @property
    def top_right(self) -> Offset:
        """Top right offset of the region.

        Returns:
            An offset.
        """
        x, y, width, _height = self
        return Offset(x + width, y)

    @property
    def bottom_right(self) -> Offset:
        """Bottom right offset of the region.

        Returns:
            An offset.
        """
        x, y, width, height = self
        return Offset(x + width, y + height)

    @property
    def size(self) -> Size:
        """Get the size of the region."""
        return Size(*self[2:])

    @property
    def corners(self) -> tuple[int, int, int, int]:
        """The top left and bottom right coordinates as a tuple of four integers."""
        x, y, width, height = self
        return x, y, x + width, y + height

    @property
    def column_range(self) -> range:
        """A range object for X coordinates."""
        return range(self.x, self.x + self.width)

    @property
    def line_range(self) -> range:
        """A range object for Y coordinates."""
        return range(self.y, self.y + self.height)

    @property
    def reset_offset(self) -> Region:
        """An region of the same size at (0, 0).

        Returns:
            A region at the origin.
        """
        _, _, width, height = self
        return Region(0, 0, width, height)

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

    def at_offset(self, offset: tuple[int, int]) -> Region:
        """Get a new Region with the same size at a given offset.

        Args:
            offset: An offset.

        Returns:
            New Region with adjusted offset.
        """
        x, y = offset
        _x, _y, width, height = self
        return Region(x, y, width, height)

    def crop_size(self, size: tuple[int, int]) -> Region:
        """Get a region with the same offset, with a size no larger than `size`.

        Args:
            size: Maximum width and height (WIDTH, HEIGHT).

        Returns:
            New region that could fit within `size`.
        """
        x, y, width1, height1 = self
        width2, height2 = size
        return Region(x, y, min(width1, width2), min(height1, height2))

    def expand(self, size: tuple[int, int]) -> Region:
        """Increase the size of the region by adding a border.

        Args:
            size: Additional width and height.

        Returns:
            A new region.
        """
        expand_width, expand_height = size
        x, y, width, height = self
        return Region(
            x - expand_width,
            y - expand_height,
            width + expand_width * 2,
            height + expand_height * 2,
        )

    def clip_size(self, size: tuple[int, int]) -> Region:
        """Clip the size to fit within minimum values.

        Args:
            size: Maximum width and height.

        Returns:
            No region, not bigger than size.
        """
        x, y, width, height = self
        max_width, max_height = size
        return Region(x, y, min(width, max_width), min(height, max_height))

    @lru_cache(maxsize=1024)
    def overlaps(self, other: Region) -> bool:
        """Check if another region overlaps this region.

        Args:
            other: A Region.

        Returns:
            True if other region shares any cells with this region.
        """
        x, y, x2, y2 = self.corners
        ox, oy, ox2, oy2 = other.corners

        return ((x2 > ox >= x) or (x2 > ox2 > x) or (ox < x and ox2 >= x2)) and (
            (y2 > oy >= y) or (y2 > oy2 > y) or (oy < y and oy2 >= y2)
        )

    def contains(self, x: int, y: int) -> bool:
        """Check if a point is in the region.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Returns:
            True if the point is within the region.
        """
        self_x, self_y, width, height = self
        return (self_x + width > x >= self_x) and (self_y + height > y >= self_y)

    def contains_point(self, point: tuple[int, int]) -> bool:
        """Check if a point is in the region.

        Args:
            point: A tuple of x and y coordinates.

        Returns:
            True if the point is within the region.
        """
        x1, y1, x2, y2 = self.corners
        try:
            ox, oy = point
        except Exception:
            raise TypeError(f"a tuple of two integers is required, not {point!r}")
        return (x2 > ox >= x1) and (y2 > oy >= y1)

    @lru_cache(maxsize=1024)
    def contains_region(self, other: Region) -> bool:
        """Check if a region is entirely contained within this region.

        Args:
            other: A region.

        Returns:
            True if the other region fits perfectly within this region.
        """
        x1, y1, x2, y2 = self.corners
        ox, oy, ox2, oy2 = other.corners
        return (
            (x2 >= ox >= x1)
            and (y2 >= oy >= y1)
            and (x2 >= ox2 >= x1)
            and (y2 >= oy2 >= y1)
        )

    @lru_cache(maxsize=1024)
    def translate(self, offset: tuple[int, int]) -> Region:
        """Move the offset of the Region.

        Args:
            offset: Offset to add to region.

        Returns:
            A new region shifted by (x, y)
        """

        self_x, self_y, width, height = self
        offset_x, offset_y = offset
        return Region(self_x + offset_x, self_y + offset_y, width, height)

    @lru_cache(maxsize=4096)
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
            width: Width of bounds.
            height: Height of bounds.

        Returns:
            Clipped region.
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

    @lru_cache(maxsize=4096)
    def grow(self, margin: tuple[int, int, int, int]) -> Region:
        """Grow a region by adding spacing.

        Args:
            margin: Grow space by `(<top>, <right>, <bottom>, <left>)`.

        Returns:
            New region.
        """
        if not any(margin):
            return self
        top, right, bottom, left = margin
        x, y, width, height = self
        return Region(
            x=x - left,
            y=y - top,
            width=max(0, width + left + right),
            height=max(0, height + top + bottom),
        )

    @lru_cache(maxsize=4096)
    def shrink(self, margin: tuple[int, int, int, int]) -> Region:
        """Shrink a region by subtracting spacing.

        Args:
            margin: Shrink space by `(<top>, <right>, <bottom>, <left>)`.

        Returns:
            The new, smaller region.
        """
        if not any(margin):
            return self
        top, right, bottom, left = margin
        x, y, width, height = self
        return Region(
            x=x + left,
            y=y + top,
            width=max(0, width - (left + right)),
            height=max(0, height - (top + bottom)),
        )

    @lru_cache(maxsize=4096)
    def intersection(self, region: Region) -> Region:
        """Get the overlapping portion of the two regions.

        Args:
            region: A region that overlaps this region.

        Returns:
            A new region that covers when the two regions overlap.
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

    @lru_cache(maxsize=4096)
    def union(self, region: Region) -> Region:
        """Get the smallest region that contains both regions.

        Args:
            region: Another region.

        Returns:
            An optimally sized region to cover both regions.
        """
        x1, y1, x2, y2 = self.corners
        ox1, oy1, ox2, oy2 = region.corners

        union_region = self.from_corners(
            min(x1, ox1), min(y1, oy1), max(x2, ox2), max(y2, oy2)
        )
        return union_region

    @lru_cache(maxsize=1024)
    def split(self, cut_x: int, cut_y: int) -> tuple[Region, Region, Region, Region]:
        """Split a region in to 4 from given x and y offsets (cuts).

        ```
                   cut_x ↓
                ┌────────┐ ┌───┐
                │        │ │   │
                │    0   │ │ 1 │
                │        │ │   │
        cut_y → └────────┘ └───┘
                ┌────────┐ ┌───┐
                │    2   │ │ 3 │
                └────────┘ └───┘
        ```

        Args:
            cut_x: Offset from self.x where the cut should be made. If negative, the cut
                is taken from the right edge.
            cut_y: Offset from self.y where the cut should be made. If negative, the cut
                is taken from the lower edge.

        Returns:
            Four new regions which add up to the original (self).
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

    @lru_cache(maxsize=1024)
    def split_vertical(self, cut: int) -> tuple[Region, Region]:
        """Split a region in to two, from a given x offset.

        ```
                 cut ↓
            ┌────────┐┌───┐
            │    0   ││ 1 │
            │        ││   │
            └────────┘└───┘
        ```

        Args:
            cut: An offset from self.x where the cut should be made. If cut is negative,
                it is taken from the right edge.

        Returns:
            Two regions, which add up to the original (self).
        """

        x, y, width, height = self
        if cut < 0:
            cut = width + cut

        return (
            Region(x, y, cut, height),
            Region(x + cut, y, width - cut, height),
        )

    @lru_cache(maxsize=1024)
    def split_horizontal(self, cut: int) -> tuple[Region, Region]:
        """Split a region in to two, from a given y offset.

        ```
                    ┌─────────┐
                    │    0    │
                    │         │
            cut →   └─────────┘
                    ┌─────────┐
                    │    1    │
                    └─────────┘
        ```

        Args:
            cut: An offset from self.y where the cut should be made. May be negative,
                for the offset to start from the lower edge.

        Returns:
            Two regions, which add up to the original (self).
        """
        x, y, width, height = self
        if cut < 0:
            cut = height + cut

        return (
            Region(x, y, width, cut),
            Region(x, y + cut, width, height - cut),
        )

    def translate_inside(
        self, container: Region, x_axis: bool = True, y_axis: bool = True
    ) -> Region:
        """Translate this region, so it fits within a container.

        This will ensure that there is as little overlap as possible.
        The top left of the returned region is guaranteed to be within the container.

        ```
        ┌──────────────────┐         ┌──────────────────┐
        │    container     │         │    container     │
        │                  │         │    ┌─────────────┤
        │                  │   ──▶   │    │    return   │
        │       ┌──────────┴──┐      │    │             │
        │       │    self     │      │    │             │
        └───────┤             │      └────┴─────────────┘
                │             │
                └─────────────┘
        ```


        Args:
            container: A container region.
            x_axis: Allow translation of X axis.
            y_axis: Allow translation of Y axis.

        Returns:
            A new region with same dimensions that fits with inside container.
        """
        x1, y1, width1, height1 = container
        x2, y2, width2, height2 = self
        return Region(
            max(min(x2, x1 + width1 - width2), x1) if x_axis else x2,
            max(min(y2, y1 + height1 - height2), y1) if y_axis else y2,
            width2,
            height2,
        )

    def inflect(
        self, x_axis: int = +1, y_axis: int = +1, margin: Spacing | None = None
    ) -> Region:
        """Inflect a region around one or both axis.

        The `x_axis` and `y_axis` parameters define which direction to move the region.
        A positive value will move the region right or down, a negative value will move
        the region left or up. A value of `0` will leave that axis unmodified.

        ```
        ╔══════════╗    │
        ║          ║
        ║   Self   ║    │
        ║          ║
        ╚══════════╝    │

        ─ ─ ─ ─ ─ ─ ─ ─ ┼ ─ ─ ─ ─ ─ ─ ─ ─

                        │    ┌──────────┐
                             │          │
                        │    │  Result  │
                             │          │
                        │    └──────────┘
        ```

        Args:
            x_axis: +1 to inflect in the positive direction, -1 to inflect in the negative direction.
            y_axis: +1 to inflect in the positive direction, -1 to inflect in the negative direction.
            margin: Additional margin.

        Returns:
            A new region.
        """
        inflect_margin = NULL_SPACING if margin is None else margin
        x, y, width, height = self
        if x_axis:
            x += (width + inflect_margin.width) * x_axis
        if y_axis:
            y += (height + inflect_margin.height) * y_axis
        return Region(x, y, width, height)


class Spacing(NamedTuple):
    """The spacing around a renderable, such as padding and border.

    Spacing is defined by four integers for the space at the top, right, bottom, and left of a region.

    ```
    ┌ ─ ─ ─ ─ ─ ─ ─▲─ ─ ─ ─ ─ ─ ─ ─ ┐
                   │ top
    │        ┏━━━━━▼━━━━━━┓         │
     ◀──────▶┃            ┃◀───────▶
    │  left  ┃            ┃ right   │
             ┃            ┃
    │        ┗━━━━━▲━━━━━━┛         │
                   │ bottom
    └ ─ ─ ─ ─ ─ ─ ─▼─ ─ ─ ─ ─ ─ ─ ─ ┘
    ```

    Example:
        ```python
        >>> from textual.geometry import Region, Spacing
        >>> region = Region(2, 3, 20, 10)
        >>> spacing = Spacing(1, 2, 3, 4)
        >>> region.grow(spacing)
        Region(x=-2, y=2, width=26, height=14)
        >>> region.shrink(spacing)
        Region(x=6, y=4, width=14, height=6)
        >>> spacing.css
        '1 2 3 4'
        ```
    """

    top: int = 0
    """Space from the top of a region."""
    right: int = 0
    """Space from the right of a region."""
    bottom: int = 0
    """Space from the bottom of a region."""
    left: int = 0
    """Space from the left of a region."""

    def __bool__(self) -> bool:
        return self != (0, 0, 0, 0)

    @property
    def width(self) -> int:
        """Total space in the x axis."""
        return self.left + self.right

    @property
    def height(self) -> int:
        """Total space in the y axis."""
        return self.top + self.bottom

    @property
    def top_left(self) -> tuple[int, int]:
        """A pair of integers for the left, and top space."""
        return (self.left, self.top)

    @property
    def bottom_right(self) -> tuple[int, int]:
        """A pair of integers for the right, and bottom space."""
        return (self.right, self.bottom)

    @property
    def totals(self) -> tuple[int, int]:
        """A pair of integers for the total horizontal and vertical space."""
        top, right, bottom, left = self
        return (left + right, top + bottom)

    @property
    def css(self) -> str:
        """A string containing the spacing in CSS format.

        For example: "1" or "2 4" or "4 2 8 2".
        """
        top, right, bottom, left = self
        if top == right == bottom == left:
            return f"{top}"
        if (top, right) == (bottom, left):
            return f"{top} {right}"
        else:
            return f"{top} {right} {bottom} {left}"

    @classmethod
    def unpack(cls, pad: SpacingDimensions) -> Spacing:
        """Unpack padding specified in CSS style.

        Args:
            pad: An integer, or tuple of 1, 2, or 4 integers.

        Raises:
            ValueError: If `pad` is an invalid value.

        Returns:
            New Spacing object.
        """
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
        raise ValueError(
            f"1, 2 or 4 integers required for spacing properties; {pad_len} given"
        )

    @classmethod
    def vertical(cls, amount: int) -> Spacing:
        """Construct a Spacing with a given amount of spacing on vertical edges,
        and no horizontal spacing.

        Args:
            amount: The magnitude of spacing to apply to vertical edges.

        Returns:
            `Spacing(amount, 0, amount, 0)`
        """
        return Spacing(amount, 0, amount, 0)

    @classmethod
    def horizontal(cls, amount: int) -> Spacing:
        """Construct a Spacing with a given amount of spacing on horizontal edges,
        and no vertical spacing.

        Args:
            amount: The magnitude of spacing to apply to horizontal edges.

        Returns:
            `Spacing(0, amount, 0, amount)`
        """
        return Spacing(0, amount, 0, amount)

    @classmethod
    def all(cls, amount: int) -> Spacing:
        """Construct a Spacing with a given amount of spacing on all edges.

        Args:
            amount: The magnitude of spacing to apply to all edges.

        Returns:
            `Spacing(amount, amount, amount, amount)`
        """
        return Spacing(amount, amount, amount, amount)

    def __add__(self, other: object) -> Spacing:
        if isinstance(other, tuple):
            top1, right1, bottom1, left1 = self
            top2, right2, bottom2, left2 = other
            return Spacing(
                top1 + top2, right1 + right2, bottom1 + bottom2, left1 + left2
            )
        return NotImplemented

    def __sub__(self, other: object) -> Spacing:
        if isinstance(other, tuple):
            top1, right1, bottom1, left1 = self
            top2, right2, bottom2, left2 = other
            return Spacing(
                top1 - top2, right1 - right2, bottom1 - bottom2, left1 - left2
            )
        return NotImplemented

    def grow_maximum(self, other: Spacing) -> Spacing:
        """Grow spacing with a maximum.

        Args:
            other: Spacing object.

        Returns:
            New spacing where the values are maximum of the two values.
        """
        top, right, bottom, left = self
        other_top, other_right, other_bottom, other_left = other
        return Spacing(
            max(top, other_top),
            max(right, other_right),
            max(bottom, other_bottom),
            max(left, other_left),
        )


NULL_OFFSET: Final = Offset(0, 0)
"""An [offset][textual.geometry.Offset] constant for (0, 0)."""

NULL_REGION: Final = Region(0, 0, 0, 0)
"""A [Region][textual.geometry.Region] constant for a null region (at the origin, with both width and height set to zero)."""

NULL_SIZE: Final = Size(0, 0)
"""A [Size][textual.geometry.Size] constant for a null size (with zero area)."""

NULL_SPACING: Final = Spacing(0, 0, 0, 0)
"""A [Spacing][textual.geometry.Spacing] constant for no space."""
