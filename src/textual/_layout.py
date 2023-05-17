from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Iterable, NamedTuple

from ._spatial_map import SpatialMap
from .geometry import Offset, Region, Size, Spacing

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    from .widget import Widget

ArrangeResult: TypeAlias = "list[WidgetPlacement]"


@dataclass
class DockArrangeResult:
    placements: list[WidgetPlacement]
    """A `WidgetPlacement` for every widget to describe it's location on screen."""
    widgets: set[Widget]
    """A set of widgets in the arrangement."""
    scroll_spacing: Spacing
    """Spacing to reduce scrollable area."""

    _spatial_map: SpatialMap[WidgetPlacement] | None = None
    """A Spatial map to query widget placements."""

    @property
    def spatial_map(self) -> SpatialMap[WidgetPlacement]:
        """A lazy-calculated spatial map."""
        if self._spatial_map is None:
            self._spatial_map = SpatialMap()
            self._spatial_map.insert(
                (
                    placement.region.grow(placement.margin),
                    placement.fixed,
                    placement.overlay,
                    placement,
                )
                for placement in self.placements
            )

        return self._spatial_map

    @property
    def total_region(self) -> Region:
        """The total area occupied by the arrangement.

        Returns:
            A Region.
        """
        _top, right, bottom, _left = self.scroll_spacing
        return self.spatial_map.total_region.grow((0, right, bottom, 0))

    def get_visible_placements(self, region: Region) -> list[WidgetPlacement]:
        """Get the placements visible within the given region.

        Args:
            region: A region.

        Returns:
            Set of placements.
        """
        visible_placements = self.spatial_map.get_values_in_region(region)
        return visible_placements


class WidgetPlacement(NamedTuple):
    """The position, size, and relative order of a widget within its parent."""

    region: Region
    margin: Spacing
    widget: Widget
    order: int = 0
    fixed: bool = False
    overlay: bool = False

    @classmethod
    def translate(
        cls, placements: list[WidgetPlacement], offset: Offset
    ) -> list[WidgetPlacement]:
        """Move all placements by a given offset.

        Args:
            placements: List of placements.
            offset: Offset to add to placements.

        Returns:
            Placements with adjusted region, or same instance if offset is null.
        """
        if offset:
            return [
                cls(region + offset, margin, layout_widget, order, fixed, overlay)
                for region, margin, layout_widget, order, fixed, overlay in placements
            ]
        return placements

    @classmethod
    def get_bounds(cls, placements: Iterable[WidgetPlacement]) -> Region:
        """Get a bounding region around all placements.

        Args:
            placements: A number of placements.

        Returns:
            An optimal binding box around all placements.
        """
        bounding_region = Region.from_union(
            [placement.region.grow(placement.margin) for placement in placements]
        )
        return bounding_region


class Layout(ABC):
    """Responsible for arranging Widgets in a view and rendering them."""

    name: ClassVar[str] = ""

    def __repr__(self) -> str:
        return f"<{self.name}>"

    @abstractmethod
    def arrange(
        self, parent: Widget, children: list[Widget], size: Size
    ) -> ArrangeResult:
        """Generate a layout map that defines where on the screen the widgets will be drawn.

        Args:
            parent: Parent widget.
            size: Size of container.

        Returns:
            An iterable of widget location
        """

    def get_content_width(self, widget: Widget, container: Size, viewport: Size) -> int:
        """Get the optimal content width by arranging children.

        Args:
            widget: The container widget.
            container: The container size.
            viewport: The viewport size.

        Returns:
            Width of the content.
        """
        if not widget._nodes:
            width = 0
        else:
            # Use a size of 0, 0 to ignore relative sizes, since those are flexible anyway
            arrangement = widget._arrange(Size(0, 0))
            return arrangement.total_region.right
        return width

    def get_content_height(
        self, widget: Widget, container: Size, viewport: Size, width: int
    ) -> int:
        """Get the content height.

        Args:
            widget: The container widget.
            container: The container size.
            viewport: The viewport.
            width: The content width.

        Returns:
            Content height (in lines).
        """
        if not widget._nodes:
            height = 0
        else:
            # Use a height of zero to ignore relative heights
            arrangement = widget._arrange(Size(width, 0))
            height = arrangement.total_region.bottom

        return height
