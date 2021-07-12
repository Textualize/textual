from __future__ import annotations

from abc import ABC, abstractmethod, abstractmethod
from dataclasses import dataclass
from itertools import chain
import logging
from operator import itemgetter
from time import time
from typing import cast, Iterable, Mapping, NamedTuple, TYPE_CHECKING

import rich.repr
from rich.control import Control
from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.segment import Segment, Segments, SegmentLines
from rich.style import Style

from ._loop import loop_last
from ._profile import timer
from ._types import Lines

from .geometry import clamp, Region, Point

log = logging.getLogger("rich")


if TYPE_CHECKING:
    from .widget import Widget, WidgetID
    from .view import View


class NoWidget(Exception):
    pass


@rich.repr.auto
class OrderedRegion(NamedTuple):
    region: Region
    order: tuple[int, int]

    def __rich_repr__(self) -> rich.repr.RichReprResult:
        yield "region", self.region
        yield "order", self.order


class ReflowResult(NamedTuple):
    """The result of a reflow operation. Describes the chances to widgets."""

    hidden: set[Widget]
    shown: set[Widget]
    resized: set[Widget]


class LayoutUpdate:
    def __init__(self, lines: Lines, x: int, y: int) -> None:
        self.lines = lines
        self.x = x
        self.y = y

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield Control.home().segment
        x = self.x
        new_line = Segment.line()
        move_to = Control.move_to
        for last, (y, line) in loop_last(enumerate(self.lines, self.y)):
            yield move_to(x, y).segment
            yield from line
            if not last:
                yield new_line


class Layout(ABC):
    """Responsible for arranging Widgets in a view."""

    def __init__(self) -> None:
        self._layout_map: dict[Widget, OrderedRegion] = {}
        self.width = 0
        self.height = 0
        self.renders: dict[Widget, tuple[Region, Lines]] = {}
        self._cuts: list[list[int]] | None = None

    def reset(self) -> None:
        self._cuts = None

    def reflow(self, width: int, height: int) -> ReflowResult:
        self.reset()

        map = self.generate_map(width, height)

        # Filter out widgets that are off screen or zero area
        screen_region = Region(0, 0, width, height)
        map = {
            widget: map_region
            for widget, map_region in map.items()
            if map_region.region and screen_region.overlaps(map_region.region)
        }

        old_widgets = set(self._layout_map.keys())
        new_widgets = set(map.keys())
        # Newly visible widgets
        shown_widgets = new_widgets - old_widgets
        # Newly hidden widgets
        hidden_widgets = old_widgets - new_widgets

        self._layout_map = map
        self.width = width
        self.height = height

        # Copy renders if the size hasn't changed
        new_renders = {
            widget: (region, self.renders[widget][1])
            for widget, (region, _order) in map.items()
            if widget in self.renders
            and self.renders[widget][0].size == region.size
            and not widget.check_repaint()
        }
        self.renders = new_renders

        # Widgets with changed size
        resized_widgets = {
            widget
            for widget, (region, _order) in map.items()
            if widget in old_widgets and widget.size != region.size
        }

        return ReflowResult(
            hidden=hidden_widgets, shown=shown_widgets, resized=resized_widgets
        )

    @abstractmethod
    def get_widgets(self) -> Iterable[Widget]:
        ...

    @abstractmethod
    def generate_map(
        self, width: int, height: int, offset: Point = Point(0, 0)
    ) -> dict[Widget, OrderedRegion]:
        ...

    async def mount_all(self, view: "View") -> None:
        await view.mount(*self.get_widgets())

    @property
    def map(self) -> dict[Widget, OrderedRegion]:
        return self._layout_map

    def __iter__(self) -> Iterable[tuple[Widget, Region]]:
        layers = sorted(
            self._layout_map.items(), key=lambda item: item[1].order, reverse=True
        )
        for widget, (region, _) in layers:
            yield widget, region

    def __reversed__(self) -> Iterable[tuple[Widget, Region]]:
        layers = sorted(self._layout_map.items(), key=lambda item: item[1].order)
        for widget, (region, _) in layers:
            yield widget, region

    def get_offset(self, widget: Widget) -> Point:
        try:
            return self._layout_map[widget].region.origin
        except KeyError:
            raise NoWidget("Widget is not in layout")

    def get_widget_at(self, x: int, y: int) -> tuple[Widget, Region]:
        """Get the widget under the given point or None."""
        for widget, region in self:
            if widget.is_visual and region.contains(x, y):
                return widget, region
        raise NoWidget(f"No widget under screen coordinate ({x}, {y})")

    def get_style_at(self, x: int, y: int) -> Style:
        try:
            widget, region = self.get_widget_at(x, y)
        except NoWidget:
            return Style.null()
        _region, lines = self.renders[widget]
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
            region, _ = self._layout_map[widget]
        except KeyError:
            raise NoWidget("Widget is not in layout")
        else:
            return region

    @property
    def cuts(self) -> list[list[int]]:
        if self._cuts is not None:
            return self._cuts
        width = self.width
        height = self.height
        screen = Region(0, 0, width, height)
        cuts_sets = [{0, width} for _ in range(height)]

        for region, order in self._layout_map.values():
            region = region.clip(width, height)
            if region and region in screen:
                for y in range(region.y, region.y + region.height):
                    cuts_sets[y].update({region.x, region.x + region.width})

        # Sort the cuts for each line
        self._cuts = [sorted(cut_set) for cut_set in cuts_sets]
        return self._cuts

    def _get_renders(self, console: Console) -> Iterable[tuple[Region, Lines]]:
        width = self.width
        height = self.height
        screen_region = Region(0, 0, width, height)
        layout_map = self._layout_map

        widget_regions = sorted(
            ((widget, region, order) for widget, (region, order) in layout_map.items()),
            key=itemgetter(2),
            reverse=True,
        )

        def render(widget: Widget, width: int, height: int) -> Lines:
            lines = console.render_lines(
                widget, console.options.update_dimensions(width, height)
            )
            return lines

        for widget, region, _order in widget_regions:

            if not widget.is_visual:
                continue
            region_lines = self.renders.get(widget)
            if region_lines is not None:
                yield region_lines
                continue

            lines = render(widget, region.width, region.height)
            if region in screen_region:
                self.renders[widget] = (region, lines)
                yield region, lines
            elif screen_region.overlaps(region):
                new_region = region.clip(width, height)
                delta_x = new_region.x - region.x
                delta_y = new_region.y - region.y
                region = new_region

                splits = [delta_x, delta_x + region.width]
                divide = Segment.divide
                lines = [
                    list(divide(line, splits))[1]
                    for line in lines[delta_y : delta_y + region.height]
                ]
                self.renders[widget] = (region, lines)
                yield region, lines

    @classmethod
    def _assemble_chops(
        cls, chops: list[dict[int, list[Segment] | None]]
    ) -> Iterable[list[Segment]]:

        for bucket in chops:
            yield sum(
                (segments for _, segments in sorted(bucket.items()) if segments),
                start=[],
            )

    def render(
        self,
        console: Console,
        clip: Region = None,
    ) -> SegmentLines:
        """Render a layout.

        Args:
            layout_map (dict[WidgetID, MapRegion]): A layout map.
            console (Console): Console instance.
            width (int): Width
            height (int): Height

        Returns:
            SegmentLines: A renderable
        """
        width = self.width
        height = self.height
        screen = Region(0, 0, width, height)
        clip = clip or screen
        clip_x, clip_y, clip_x2, clip_y2 = clip.corners

        divide = Segment.divide
        back = Style.parse("black")

        # Maps each cut on to a list of segments
        cuts = self.cuts
        chops: list[dict[int, list[Segment] | None]] = [
            {cut: None for cut in cut_set} for cut_set in cuts
        ]

        # TODO: Provide an option to update the background
        background_render = [[Segment(" " * width, back)] for _ in range(height)]
        # Go through all the renders in reverse order and fill buckets with no render
        renders = self._get_renders(console)
        for region, lines in chain(renders, [(screen, background_render)]):
            for y, line in enumerate(lines, region.y):
                if clip_y > y > clip_y2:
                    continue
                first_cut = clamp(region.x, clip_x, clip_x2)
                last_cut = clamp(region.x + region.width, clip_x, clip_x2)
                final_cuts = [cut for cut in cuts[y] if (last_cut >= cut >= first_cut)]
                if len(final_cuts) > 1:
                    if final_cuts == [region.x, region.x + region.width]:
                        cut_segments = [line]
                    else:
                        relative_cuts = [cut - region.x for cut in final_cuts]
                        _, *cut_segments = divide(line, relative_cuts)
                    for cut, segments in zip(final_cuts, cut_segments):
                        if chops[y][cut] is None:
                            chops[y][cut] = segments

        # Assemble the cut renders in to lists of segments
        output_lines = list(self._assemble_chops(chops[clip_y:clip_y2]))
        return SegmentLines(output_lines, new_lines=True)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield self.render(console)

    def update_widget(self, console: Console, widget: Widget) -> LayoutUpdate | None:
        if widget not in self.renders:
            return None
        region, lines = self.renders[widget]
        new_lines = console.render_lines(
            widget, console.options.update_dimensions(region.width, region.height)
        )
        self.renders[widget] = (region, new_lines)

        update_lines = self.render(console, region).lines
        return LayoutUpdate(update_lines, region.x, region.y)
