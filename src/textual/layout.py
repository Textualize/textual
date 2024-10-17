from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Iterable, NamedTuple

from textual._spatial_map import SpatialMap
from textual.canvas import Canvas, Rectangle
from textual.geometry import Offset, Region, Size, Spacing
from textual.strip import StripRenderable

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    from textual.widget import Widget

ArrangeResult: TypeAlias = "list[WidgetPlacement]"


@dataclass
class DockArrangeResult:
    """Result of [Layout.arrange][textual.layout.Layout.arrange]."""

    placements: list[WidgetPlacement]
    """A `WidgetPlacement` for every widget to describe its location on screen."""
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
        if self.total_region in region:
            # Short circuit for when we want all the placements
            return self.placements
        visible_placements = self.spatial_map.get_values_in_region(region)
        overlaps = region.overlaps
        culled_placements = [
            placement
            for placement in visible_placements
            if placement.fixed or overlaps(placement.region)
        ]
        return culled_placements


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
    """Base class of the object responsible for arranging Widgets within a container."""

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
            arrangement = widget._arrange(
                Size(0 if widget.shrink else container.width, 0)
            )
            width = arrangement.total_region.right
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
            styles_height = widget.styles.height
            if widget._parent and len(widget._nodes) == 1:
                # If it is an only child with height auto we want it to expand
                height = (
                    container.height
                    if styles_height is not None and styles_height.is_auto
                    else 0
                )
            else:
                height = 0
            arrangement = widget._arrange(Size(width, height))
            height = arrangement.total_region.bottom

        return height

    def render_keyline(self, container: Widget) -> StripRenderable:
        """Render keylines around all widgets.

        Args:
            container: The container widget.

        Returns:
            A renderable to draw the keylines.
        """
        width, height = container.outer_size
        canvas = Canvas(width, height)

        line_style, keyline_color = container.styles.keyline
        if keyline_color:
            keyline_color = container.background_colors[0] + keyline_color

        container_offset = container.content_region.offset

        def get_rectangle(region: Region) -> Rectangle:
            """Get a canvas Rectangle that wraps a region.

            Args:
                region: Widget region.

            Returns:
                A Rectangle that encloses the widget.
            """
            offset = region.offset - container_offset - (1, 1)
            width, height = region.size
            return Rectangle(offset, width + 2, height + 2, keyline_color, line_style)

        primitives = [
            get_rectangle(widget.region)
            for widget in container.children
            if widget.visible
        ]
        canvas_renderable = canvas.render(primitives, container.rich_style)
        return canvas_renderable
