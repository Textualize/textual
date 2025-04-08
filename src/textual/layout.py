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
                    placement.offset,
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
            if placement.fixed or overlaps(placement.region + placement.offset)
        ]
        return culled_placements


class WidgetPlacement(NamedTuple):
    """The position, size, and relative order of a widget within its parent."""

    region: Region
    offset: Offset
    margin: Spacing
    widget: Widget
    order: int = 0
    fixed: bool = False
    overlay: bool = False
    absolute: bool = False

    @property
    def reset_origin(self) -> WidgetPlacement:
        """Reset the origin in the placement (moves it to (0, 0))."""
        return self._replace(region=self.region.reset_offset)

    @classmethod
    def translate(
        cls, placements: list[WidgetPlacement], translate_offset: Offset
    ) -> list[WidgetPlacement]:
        """Move all non-absolute placements by a given offset.

        Args:
            placements: List of placements.
            offset: Offset to add to placements.

        Returns:
            Placements with adjusted region, or same instance if offset is null.
        """
        if translate_offset:
            return [
                cls(
                    (
                        region + translate_offset
                        if layout_widget.absolute_offset is None
                        else region
                    ),
                    offset,
                    margin,
                    layout_widget,
                    order,
                    fixed,
                    overlay,
                    absolute,
                )
                for region, offset, margin, layout_widget, order, fixed, overlay, absolute in placements
            ]
        return placements

    @classmethod
    def apply_absolute(cls, placements: list[WidgetPlacement]) -> None:
        """Applies absolute offsets (in place).

        Args:
            placements: A list of placements.
        """
        for index, placement in enumerate(placements):
            if placement.absolute:
                placements[index] = placement.reset_origin

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

    def process_offset(
        self, constrain_region: Region, absolute_offset: Offset
    ) -> WidgetPlacement:
        """Apply any absolute offset or constrain rules to the placement.

        Args:
            constrain_region: The container region when applying constrain rules.
            absolute_offset: Default absolute offset that moves widget into screen coordinates.

        Returns:
            Processes placement, may be the same instance.
        """
        widget = self.widget
        styles = widget.styles
        if not widget.absolute_offset and not styles.has_any_rules(
            "constrain_x", "constrain_y"
        ):
            # Bail early if there is nothing to do
            return self
        region = self.region
        margin = self.margin
        if widget.absolute_offset is not None:
            region = region.at_offset(
                widget.absolute_offset + margin.top_left - absolute_offset
            )

        region = region.translate(self.offset).constrain(
            styles.constrain_x,
            styles.constrain_y,
            self.margin,
            constrain_region - absolute_offset,
        )

        offset = region.offset - self.region.offset
        if offset != self.offset:
            region, _offset, margin, widget, order, fixed, overlay, absolute = self
            placement = WidgetPlacement(
                region, offset, margin, widget, order, fixed, overlay, absolute
            )
            return placement
        return self


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
        if widget._nodes:
            if not widget.styles.is_docked and all(
                child.styles.is_dynamic_height for child in widget.displayed_children
            ):
                # An exception for containers with all dynamic height widgets
                arrangement = widget._arrange(Size(width, container.height))
            else:
                arrangement = widget._arrange(Size(width, 0))
            height = arrangement.total_region.height
        else:
            height = 0
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
