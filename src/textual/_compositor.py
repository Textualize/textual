"""

The compositor handles combining widgets in to a single screen (i.e. compositing).

It also stores the results of that process, so that Textual knows the widgets on
the screen and their locations. The compositor uses this information to answer
queries regarding the widget under an offset, or the style under an offset.

Additionally, the compositor can render portions of the screen which may have updated,
without having to render the entire screen.

"""

from __future__ import annotations

from itertools import chain
from operator import attrgetter, itemgetter
import sys
from typing import Callable, cast, Iterator, Iterable, NamedTuple, TYPE_CHECKING

import rich.repr
from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.control import Control
from rich.segment import Segment
from rich.style import Style

from . import errors
from .geometry import Region, Offset, Size

from ._profile import timer
from ._loop import loop_last
from ._segment_tools import line_crop
from ._types import Lines

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:  # pragma: no cover
    from typing_extensions import TypeAlias


if TYPE_CHECKING:
    from .widget import Widget


class ReflowResult(NamedTuple):
    """The result of a reflow operation. Describes the chances to widgets."""

    hidden: set[Widget]  # Widgets that are hidden
    shown: set[Widget]  # Widgets that are shown
    resized: set[Widget]  # Widgets that have been resized


class MapGeometry(NamedTuple):
    """Defines the absolute location of a Widget."""

    region: Region  # The region occupied by the widget
    order: tuple[int, ...]  # A tuple of ints defining the painting order
    clip: Region  # A region to clip the widget by (if a Widget is within a container)
    virtual_size: Size  # The virtual size  (scrollable region) of a widget if it is a container
    container_size: Size  # The container size (area not occupied by scrollbars)

    @property
    def visible_region(self) -> Region:
        """The Widget region after clipping."""
        return self.clip.intersection(self.region)


# Maps a widget on to its geometry (information that describes its position in the composition)
CompositorMap: TypeAlias = "dict[Widget, MapGeometry]"


@rich.repr.auto(angular=True)
class LayoutUpdate:
    """A renderable containing the result of a render for a given region."""

    def __init__(self, lines: Lines, region: Region) -> None:
        self.lines = lines
        self.region = region

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        x = self.region.x
        new_line = Segment.line()
        move_to = Control.move_to
        for last, (y, line) in loop_last(enumerate(self.lines, self.region.y)):
            yield move_to(x, y)
            yield from line
            if not last:
                yield new_line

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.region


@rich.repr.auto(angular=True)
class ChopsUpdate:
    """A renderable that applies updated spans to the screen."""

    def __init__(
        self, chops: list[dict[int, list[Segment] | None]], crop: Region
    ) -> None:
        """A renderable which updates chops (fragments of lines).

        Args:
            chops (list[dict[int, list[Segment]  |  None]]): A mapping of offsets to list of segments, per line.
            crop (Region): Region to restrict update to.
        """
        self.chops = chops
        self.crop = crop

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        move_to = Control.move_to
        new_line = Segment.line()
        chops = self.chops
        crop = self.crop
        last_y = crop.y_max - 1
        x1, x2 = crop.x_extents
        for y in crop.y_range:
            line = chops[y]
            for x, segments in line.items():
                if segments is not None and x2 > x >= x1:
                    yield move_to(x, y)
                    yield from segments
            if y != last_y:
                yield new_line

    def __rich_repr__(self) -> rich.repr.Result:
        yield None, self.crop


@rich.repr.auto(angular=True)
class Compositor:
    """Responsible for storing information regarding the relative positions of Widgets and rendering them."""

    def __init__(self) -> None:
        # A mapping of Widget on to its "render location" (absolute position / depth)
        self.map: CompositorMap = {}

        # All widgets considered in the arrangement
        # Note this may be a superset of self.map.keys() as some widgets may be invisible for various reasons
        self.widgets: set[Widget] = set()

        # The top level widget
        self.root: Widget | None = None

        # Dimensions of the arrangement
        self.size = Size(0, 0)

        # A mapping of Widget on to region, and clip region
        # The clip region can be considered the window through which a widget is viewed
        self.regions: dict[Widget, tuple[Region, Region]] = {}

        # The points in each line where the line bisects the left and right edges of the widget
        self._cuts: list[list[int]] | None = None

        # Regions that require an update
        self._dirty_regions: set[Region] = set()

    def add_dirty_regions(self, regions: Iterable[Region]) -> None:
        """Add dirty regions to be repainted next call to render.

        Args:
            regions (Iterable[Region]): Regions that are "dirty" (changed since last render).
        """
        self._dirty_regions.update(regions)

    @classmethod
    def _regions_to_spans(
        cls, regions: Iterable[Region]
    ) -> Iterable[tuple[int, int, int]]:
        """Converts the regions to horizontal spans. Spans will be combined if they overlap
        or are contiguous to produce optimal non-overlapping spans.

        Args:
            regions (Iterable[Region]): An iterable of Regions.

        Returns:
            Iterable[tuple[int, int, int]]: Yields tuples of (Y, X1, X2)
        """
        inline_ranges: dict[int, list[tuple[int, int]]] = {}
        setdefault = inline_ranges.setdefault
        for region_x, region_y, width, height in regions:
            span = (region_x, region_x + width)
            for y in range(region_y, region_y + height):
                setdefault(y, []).append(span)

        for y, ranges in sorted(inline_ranges.items()):
            if len(ranges) == 1:
                # Special case of 1 span
                yield (y, *ranges[0])
            else:
                ranges.sort()
                x1, x2 = ranges[0]
                for next_x1, next_x2 in ranges[1:]:
                    if next_x1 <= x2:
                        if next_x2 > x2:
                            x2 = next_x2
                    else:
                        yield (y, x1, x2)
                        x1 = next_x1
                        x2 = next_x2
                yield (y, x1, x2)

    def __rich_repr__(self) -> rich.repr.Result:
        yield "size", self.size
        yield "widgets", self.widgets

    def reflow(self, parent: Widget, size: Size) -> ReflowResult:
        """Reflow (layout) widget and its children.

        Args:
            parent (Widget): The root widget.
            size (Size): Size of the area to be filled.

        Returns:
            ReflowResult: Hidden shown and resized widgets
        """
        self._cuts = None
        self.root = parent
        self.size = size

        # Keep a copy of the old map because we're going to compare it with the update
        old_map = self.map.copy()
        old_widgets = old_map.keys()
        map, widgets = self._arrange_root(parent, size)

        new_widgets = map.keys()

        # Newly visible widgets
        shown_widgets = new_widgets - old_widgets
        # Newly hidden widgets
        hidden_widgets = old_widgets - new_widgets

        # Replace map and widgets
        self.map = map
        self.widgets = widgets

        # Get a map of regions
        self.regions = {
            widget: (region, clip)
            for widget, (region, _order, clip, _, _) in map.items()
        }

        # Widgets with changed size
        resized_widgets = {
            widget
            for widget, (region, *_) in map.items()
            if widget in old_widgets and old_map[widget].region.size != region.size
        }

        # Gets pairs of tuples of (Widget, MapGeometry) which have changed
        # i.e. if something is moved / deleted / added
        screen = size.region

        if screen not in self._dirty_regions:
            crop_screen = screen.intersection
            changes = map.items() ^ old_map.items()
            regions = {
                region
                for region in (
                    crop_screen(map_geometry.visible_region)
                    for _, map_geometry in changes
                )
                if region
            }
            self._dirty_regions.update(regions)

        return ReflowResult(
            hidden=hidden_widgets,
            shown=shown_widgets,
            resized=resized_widgets,
        )

    def _arrange_root(
        self, root: Widget, size: Size
    ) -> tuple[CompositorMap, set[Widget]]:
        """Arrange a widgets children based on its layout attribute.

        Args:
            root (Widget): Top level widget.

        Returns:
            map[dict[Widget, RenderRegion], Size]: A mapping of widget on to render region
                and the "virtual size" (scrollable region)
        """

        ORIGIN = Offset(0, 0)

        map: CompositorMap = {}
        widgets: set[Widget] = set()
        get_order = attrgetter("order")

        def add_widget(
            widget: Widget,
            region: Region,
            order: tuple[int, ...],
            clip: Region,
        ) -> None:
            """Called recursively to place a widget and its children in the map.

            Args:
                widget (Widget): The widget to add.
                region (Region): The region the widget will occupy.
                order (tuple[int, ...]): A tuple of ints to define the order.
                clip (Region): The clipping region (i.e. the viewport which contains it).
            """
            widgets.add(widget)
            styles_offset = widget.styles.offset
            layout_offset = (
                styles_offset.resolve(region.size, clip.size)
                if styles_offset
                else ORIGIN
            )

            # Container region is minus border
            container_region = region.shrink(widget.styles.gutter)
            container_size = container_region.size

            # Widgets with scrollbars (containers or scroll view) require additional processing
            if widget.is_scrollable:
                # The region that contains the content (container region minus scrollbars)
                child_region = widget._get_scrollable_region(container_region)

                # Adjust the clip region accordingly
                sub_clip = clip.intersection(child_region)

                # The region covered by children relative to parent widget
                total_region = child_region.reset_origin

                if widget.is_container:
                    # Arrange the layout
                    placements, arranged_widgets = widget._arrange(child_region.size)
                    widgets.update(arranged_widgets)
                    placements = sorted(placements, key=get_order)

                    # An offset added to all placements
                    placement_offset = (
                        container_region.origin + layout_offset - widget.scroll_offset
                    )

                    # Add all the widgets
                    for sub_region, sub_widget, z in placements:
                        # Combine regions with children to calculate the "virtual size"
                        total_region = total_region.union(sub_region)
                        if sub_widget is not None:
                            add_widget(
                                sub_widget,
                                sub_region + placement_offset,
                                order + (z,),
                                sub_clip,
                            )

                # Add any scrollbars
                for chrome_widget, chrome_region in widget._arrange_scrollbars(
                    container_size
                ):
                    map[chrome_widget] = MapGeometry(
                        chrome_region + container_region.origin + layout_offset,
                        order,
                        clip,
                        container_size,
                        container_size,
                    )

                if widget.is_container:
                    # Add the container widget, which will render a background
                    map[widget] = MapGeometry(
                        region + layout_offset,
                        order,
                        clip,
                        total_region.size,
                        container_size,
                    )
                else:
                    map[widget] = MapGeometry(
                        child_region + layout_offset,
                        order,
                        clip,
                        child_region.size,
                        container_size,
                    )

            else:
                # Add the widget to the map
                map[widget] = MapGeometry(
                    region + layout_offset, order, clip, region.size, container_size
                )

        # Add top level (root) widget
        add_widget(root, size.region, (0,), size.region)
        return map, widgets

    def __iter__(self) -> Iterator[tuple[Widget, Region, Region, Size, Size]]:
        """Iterate map with information regarding each widget and is position

        Yields:
            Iterator[tuple[Widget, Region, Region, Size, Size]]: Iterates a tuple of
                Widget, clip region, region, virtual size, and container size.
        """
        layers = sorted(self.map.items(), key=lambda item: item[1].order, reverse=True)
        intersection = Region.intersection
        for widget, (region, _order, clip, virtual_size, container_size) in layers:
            yield (
                widget,
                intersection(region, clip),
                region,
                virtual_size,
                container_size,
            )

    def get_offset(self, widget: Widget) -> Offset:
        """Get the offset of a widget."""
        try:
            return self.map[widget].region.origin
        except KeyError:
            raise errors.NoWidget("Widget is not in layout")

    def get_widget_at(self, x: int, y: int) -> tuple[Widget, Region]:
        """Get the widget under the given point or None."""
        contains = Region.contains
        for widget, cropped_region, region, *_ in self:
            if contains(cropped_region, x, y):
                return widget, region
        raise errors.NoWidget(f"No widget under screen coordinate ({x}, {y})")

    def get_style_at(self, x: int, y: int) -> Style:
        """Get the Style at the given cell or Style.null()

        Args:
            x (int): X position within the Layout
            y (int): Y position within the Layout

        Returns:
            Style: The Style at the cell (x, y) within the Layout
        """
        try:
            widget, region = self.get_widget_at(x, y)
        except errors.NoWidget:
            return Style.null()
        if widget not in self.regions:
            return Style.null()

        x -= region.x
        y -= region.y

        lines = widget.render_lines(Region(0, y, region.width, 1))

        if not lines:
            return Style.null()
        end = 0
        for segment in lines[0]:
            end += segment.cell_length
            if x < end:
                return segment.style or Style.null()
        return Style.null()

    def find_widget(self, widget: Widget) -> MapGeometry:
        """Get information regarding the relative position of a widget in the Compositor.

        Args:
            widget (Widget): The Widget in this layout you wish to know the Region of.

        Raises:
            NoWidget: If the Widget is not contained in this Layout.

        Returns:
            MapGeometry: Widget's composition information.

        """
        try:
            region = self.map[widget]
        except KeyError:
            raise errors.NoWidget("Widget is not in layout")
        else:
            return region

    @property
    def cuts(self) -> list[list[int]]:
        """Get vertical cuts.

        A cut is every point on a line where a widget starts or ends.

        Returns:
            list[list[int]]: A list of cuts for every line.
        """
        if self._cuts is not None:
            return self._cuts

        width, height = self.size
        screen_region = self.size.region
        cuts = [[0, width] for _ in range(height)]

        intersection = Region.intersection
        extend = list.extend

        for region, order, clip, _, _ in self.map.values():
            region = intersection(region, clip)
            if region and (region in screen_region):
                x, y, region_width, region_height = region
                region_cuts = (x, x + region_width)
                for cut in cuts[y : y + region_height]:
                    extend(cut, region_cuts)

        # Sort the cuts for each line
        self._cuts = [sorted(set(line_cuts)) for line_cuts in cuts]
        return self._cuts

    def _get_renders(
        self, crop: Region | None = None
    ) -> Iterable[tuple[Region, Region, Lines]]:
        """Get rendered widgets (lists of segments) in the composition.

        Returns:
            Iterable[tuple[Region, Region, Lines]]: An iterable of <region>, <clip region>, and <lines>
        """
        # If a renderable throws an error while rendering, the user likely doesn't care about the traceback
        # up to this point.
        _rich_traceback_guard = True

        if self.map:
            if crop:
                overlaps = crop.overlaps
                mapped_regions = [
                    (widget, region, order, clip)
                    for widget, (region, order, clip, _, _) in self.map.items()
                    if widget.visible and not widget.is_transparent and overlaps(crop)
                ]
            else:
                mapped_regions = [
                    (widget, region, order, clip)
                    for widget, (region, order, clip, _, _) in self.map.items()
                    if widget.visible and not widget.is_transparent
                ]

            widget_regions = sorted(mapped_regions, key=itemgetter(2), reverse=True)
        else:
            widget_regions = []

        intersection = Region.intersection
        overlaps = Region.overlaps

        for widget, region, _order, clip in widget_regions:
            if not region:
                continue
            if region in clip:
                yield region, clip, widget.render_lines(
                    Region(0, 0, region.width, region.height)
                )
            elif overlaps(clip, region):
                clipped_region = intersection(region, clip)
                if not clipped_region:
                    continue
                new_x, new_y, new_width, new_height = clipped_region
                delta_x = new_x - region.x
                delta_y = new_y - region.y
                lines = widget.render_lines(
                    Region(delta_x, delta_y, new_width, new_height)
                )
                yield region, clip, lines

    @classmethod
    def _assemble_chops(
        cls, chops: list[dict[int, list[Segment] | None]]
    ) -> list[list[Segment]]:
        """Combine chops in to lines."""
        from_iterable = chain.from_iterable
        segment_lines: list[list[Segment]] = [
            list(from_iterable(line for line in bucket.values() if line is not None))
            for bucket in chops
        ]
        return segment_lines

    @timer("render")
    def render(self, full: bool = False) -> RenderableType | None:
        """Render a layout.

        Returns:
            SegmentLines: A renderable
        """
        width, height = self.size
        screen_region = Region(0, 0, width, height)

        if full:
            update_regions: set[Region] = set()
        else:
            update_regions = self._dirty_regions.copy()
            if screen_region in update_regions:
                # If one of the updates is the entire screen, then we only need one update
                full = True
        self._dirty_regions.clear()

        if full:
            crop = screen_region
            spans = []
            is_rendered_line = lambda y: True
        elif update_regions:
            # Create a crop regions that surrounds all updates
            crop = Region.from_union(update_regions).intersection(screen_region)
            spans = list(self._regions_to_spans(update_regions))
            is_rendered_line = {y for y, _, _ in spans}.__contains__
        else:
            return None

        divide = Segment.divide

        # Maps each cut on to a list of segments
        cuts = self.cuts

        # dict.fromkeys is a callable which takes a list of ints returns a dict which maps ints on to a list of Segments or None.
        fromkeys = cast(
            "Callable[[list[int]], dict[int, list[Segment] | None]]", dict.fromkeys
        )
        # A mapping of cut index to a list of segments for each line
        chops: list[dict[int, list[Segment] | None]]
        chops = [fromkeys(cut_set) for cut_set in cuts]

        cut_segments: Iterable[list[Segment]]

        # Go through all the renders in reverse order and fill buckets with no render
        renders = self._get_renders(crop)
        intersection = Region.intersection

        for region, clip, lines in renders:
            render_region = intersection(region, clip)

            for y, line in zip(render_region.y_range, lines):
                if not is_rendered_line(y):
                    continue

                chops_line = chops[y]
                if all(chops_line):
                    continue

                first_cut, last_cut = render_region.x_extents
                final_cuts = [cut for cut in cuts[y] if (last_cut >= cut >= first_cut)]

                if len(final_cuts) <= 2:
                    # Two cuts, which means the entire line
                    cut_segments = [line]
                else:
                    render_x = render_region.x
                    relative_cuts = [cut - render_x for cut in final_cuts[1:]]
                    cut_segments = divide(line, relative_cuts)

                # Since we are painting front to back, the first segments for a cut "wins"
                for cut, segments in zip(final_cuts, cut_segments):
                    if chops_line[cut] is None:
                        chops_line[cut] = segments

        if full:
            render_lines = self._assemble_chops(chops)
            return LayoutUpdate(render_lines, screen_region)
        else:
            return ChopsUpdate(chops, crop)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        if self._dirty_regions:
            yield self.render()

    def update_widgets(self, widgets: set[Widget]) -> None:
        """Update a given widget in the composition.

        Args:
            console (Console): Console instance.
            widget (Widget): Widget to update.

        """
        regions: list[Region] = []
        add_region = regions.append
        for widget in self.regions.keys() & widgets:
            region, clip = self.regions[widget]
            update_region = region.intersection(clip)
            if update_region:
                add_region(update_region)
        self.add_dirty_regions(regions)
