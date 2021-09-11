from __future__ import annotations

from abc import ABC, abstractmethod, abstractmethod
from dataclasses import dataclass
from itertools import chain
from operator import itemgetter
import sys

from typing import Iterable, Iterator, NamedTuple, TYPE_CHECKING
from rich import segment

import rich.repr
from rich.control import Control
from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.segment import Segment, SegmentLines
from rich.style import Style

from . import log, panic
from ._loop import loop_last
from .layout_map import LayoutMap
from ._profile import timer
from ._lines import crop_lines
from ._types import Lines

from .geometry import clamp, Region, Offset, Size


PY38 = sys.version_info >= (3, 8)


if TYPE_CHECKING:
    from .widget import Widget
    from .view import View


class NoWidget(Exception):
    pass


class OrderedRegion(NamedTuple):
    region: Region
    order: tuple[int, int]


class ReflowResult(NamedTuple):
    """The result of a reflow operation. Describes the chances to widgets."""

    hidden: set[Widget]
    shown: set[Widget]
    resized: set[Widget]


class WidgetPlacement(NamedTuple):

    region: Region
    widget: Widget | None = None
    order: tuple[int, ...] = ()


@rich.repr.auto
class LayoutUpdate:
    def __init__(self, lines: Lines, region: Region) -> None:
        self.lines = lines
        self.region = region

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield Control.home().segment
        x = self.region.x
        new_line = Segment.line()
        move_to = Control.move_to
        for last, (y, line) in loop_last(enumerate(self.lines, self.region.y)):
            yield move_to(x, y).segment
            yield from line
            if not last:
                yield new_line

    def __rich_repr__(self) -> rich.repr.Result:
        x, y, width, height = self.region
        yield "x", x
        yield "y", y
        yield "width", width
        yield "height", height


class Layout(ABC):
    """Responsible for arranging Widgets in a view and rendering them."""

    def __init__(self) -> None:
        self._layout_map: LayoutMap | None = None
        self.width = 0
        self.height = 0
        self.regions: dict[Widget, tuple[Region, Region]] = {}
        self._cuts: list[list[int]] | None = None
        self._require_update: bool = True
        self.background = ""

    def check_update(self) -> bool:
        return self._require_update

    def require_update(self) -> None:
        self._require_update = True
        self.reset()
        self._layout_map = None

    def reset_update(self) -> None:
        self._require_update = False

    def reset(self) -> None:
        self._cuts = None

    def reflow(self, view: View, size: Size) -> ReflowResult:
        self.reset()

        self.width = size.width
        self.height = size.height

        map = LayoutMap(size)
        map.add_widget(view, size.region, (), size.region)

        self._require_update = False

        old_widgets = set() if self.map is None else set(self.map.keys())
        new_widgets = set(map.keys())
        # Newly visible widgets
        shown_widgets = new_widgets - old_widgets
        # Newly hidden widgets
        hidden_widgets = old_widgets - new_widgets

        self._layout_map = map

        # Copy renders if the size hasn't changed
        new_renders = {
            widget: (region, clip) for widget, (region, _order, clip) in map.items()
        }
        self.regions = new_renders

        # Widgets with changed size
        resized_widgets = {
            widget
            for widget, (region, *_) in map.items()
            if widget in old_widgets and widget.size != region.size
        }

        return ReflowResult(
            hidden=hidden_widgets, shown=shown_widgets, resized=resized_widgets
        )

    @abstractmethod
    def get_widgets(self) -> Iterable[Widget]:
        ...

    @abstractmethod
    def arrange(self, size: Size, scroll: Offset) -> Iterable[WidgetPlacement]:
        """Generate a layout map that defines where on the screen the widgets will be drawn.

        Args:
            console (Console): Console instance.
            size (Dimensions): Size of container.
            viewport (Region): Screen relative viewport.

        Returns:
            Iterable[WidgetPlacement]: An iterable of widget location
        """

    async def mount_all(self, view: "View") -> None:
        await view.mount(*self.get_widgets())

    @property
    def map(self) -> LayoutMap | None:
        return self._layout_map

    def __iter__(self) -> Iterator[tuple[Widget, Region, Region]]:
        if self.map is not None:
            layers = sorted(
                self.map.widgets.items(), key=lambda item: item[1].order, reverse=True
            )
            for widget, (region, order, clip) in layers:
                yield widget, region.intersection(clip), region

    def get_offset(self, widget: Widget) -> Offset:
        """Get the offset of a widget."""
        try:
            return self.map[widget].region.origin
        except KeyError:
            raise NoWidget("Widget is not in layout")

    def get_widget_at(self, x: int, y: int) -> tuple[Widget, Region]:
        """Get the widget under the given point or None."""
        for widget, cropped_region, region in self:
            if widget.is_visual and cropped_region.contains(x, y):
                return widget, region
        raise NoWidget(f"No widget under screen coordinate ({x}, {y})")

    def get_style_at(self, x: int, y: int) -> Style:
        try:
            widget, region = self.get_widget_at(x, y)
        except NoWidget:
            return Style.null()
        if widget not in self.regions:
            return Style.null()
        lines = widget._get_lines()
        x -= region.x
        y -= region.y
        line = lines[y]
        end = 0
        for segment in line:
            end += segment.cell_length
            if x < end:
                return segment.style or Style.null()
        return Style.null()

    def get_widget_region(self, widget: Widget) -> Region:
        try:
            region, *_ = self.map[widget]
        except KeyError:
            raise NoWidget("Widget is not in layout")
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
        width = self.width
        height = self.height
        screen_region = Region(0, 0, width, height)
        cuts_sets = [{0, width} for _ in range(height)]

        if self.map is not None:
            for region, order, clip in self.map.values():
                region = region.intersection(clip)
                if region and (region in screen_region):
                    region_cuts = region.x_extents
                    for y in region.y_range:
                        cuts_sets[y].update(region_cuts)

        # Sort the cuts for each line
        self._cuts = [sorted(cut_set) for cut_set in cuts_sets]
        return self._cuts

    def _get_renders(self, console: Console) -> Iterable[tuple[Region, Region, Lines]]:
        _rich_traceback_guard = True
        layout_map = self.map

        if layout_map:
            widget_regions = sorted(
                (
                    (widget, region, order, clip)
                    for widget, (region, order, clip) in layout_map.items()
                ),
                key=itemgetter(2),
                reverse=True,
            )
        else:
            widget_regions = []

        for widget, region, _order, clip in widget_regions:

            if not widget.is_visual:
                continue

            lines = widget._get_lines()

            if region in clip:
                yield region, clip, lines
            elif clip.overlaps(region):
                new_region = region.intersection(clip)
                delta_x = new_region.x - region.x
                delta_y = new_region.y - region.y
                splits = [delta_x, delta_x + new_region.width]
                lines = lines[delta_y : delta_y + new_region.height]
                divide = Segment.divide
                lines = [list(divide(line, splits))[1] for line in lines]
                yield region, clip, lines

    @classmethod
    def _assemble_chops(
        cls, chops: list[dict[int, list[Segment] | None]]
    ) -> Iterable[list[Segment]]:

        from_iterable = chain.from_iterable
        for bucket in chops:
            yield from_iterable(
                line for _, line in sorted(bucket.items()) if line is not None
            )

    def render(
        self,
        console: Console,
        *,
        crop: Region = None,
    ) -> SegmentLines:
        """Render a layout.

        Args:
            console (Console): Console instance.
            clip (Optional[Region]): Region to clip to.

        Returns:
            SegmentLines: A renderable
        """
        width = self.width
        height = self.height
        screen = Region(0, 0, width, height)

        crop_region = crop.intersection(screen) if crop else screen

        _Segment = Segment
        divide = _Segment.divide

        # Maps each cut on to a list of segments
        cuts = self.cuts
        chops: list[dict[int, list[Segment] | None]] = [
            {cut: None for cut in cut_set} for cut_set in cuts
        ]

        # TODO: Provide an option to update the background
        background_style = console.get_style(self.background)
        background_render = [
            [_Segment(" " * width, background_style)] for _ in range(height)
        ]
        # Go through all the renders in reverse order and fill buckets with no render
        renders = list(self._get_renders(console))

        for region, clip, lines in chain(
            renders, [(screen, screen, background_render)]
        ):
            render_region = region.intersection(clip)
            for y, line in zip(render_region.y_range, lines):

                first_cut, last_cut = render_region.x_extents
                final_cuts = [cut for cut in cuts[y] if (last_cut >= cut >= first_cut)]

                if len(final_cuts) == 2:
                    cut_segments = [line]
                else:
                    render_x = render_region.x
                    relative_cuts = [cut - render_x for cut in final_cuts]
                    _, *cut_segments = divide(line, relative_cuts)
                for cut, segments in zip(final_cuts, cut_segments):
                    if chops[y][cut] is None:
                        chops[y][cut] = segments

        # Assemble the cut renders in to lists of segments
        crop_x, crop_y, crop_x2, crop_y2 = crop_region.corners
        output_lines = self._assemble_chops(chops[crop_y:crop_y2])

        def width_view(line: list[Segment]) -> list[Segment]:
            if line:
                div_lines = list(divide(line, [crop_x, crop_x2]))
                line = div_lines[1] if len(div_lines) > 1 else div_lines[0]
            return line

        if crop is not None and (crop_x, crop_x2) != (0, self.width):
            render_lines = [width_view(line) for line in output_lines]
        else:
            render_lines = list(output_lines)

        return SegmentLines(render_lines, new_lines=True)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield self.render(console)

    def update_widget(self, console: Console, widget: Widget) -> LayoutUpdate | None:
        if widget not in self.regions:
            return None

        region, clip = self.regions[widget]

        if not region.size:
            return None

        widget.clear_render_cache()

        update_region = region.intersection(clip)
        update_lines = self.render(console, crop=update_region).lines
        update = LayoutUpdate(update_lines, update_region)
        return update
