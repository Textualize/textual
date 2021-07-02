from __future__ import annotations

from abc import ABC, abstractmethod, abstractmethod
from dataclasses import dataclass
from itertools import chain
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

from .geometry import clamp, Region


if TYPE_CHECKING:
    from .widget import WidgetBase, WidgetID


class MapRegion(NamedTuple):
    region: Region
    order: tuple[int, int]


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
        for y, line in enumerate(self.lines, self.y):
            yield move_to(x, y).segment
            yield from line
            yield new_line


class Layout(ABC):
    """Responsible for rendering a layout."""

    def __init__(self) -> None:
        self._layout_map: dict[WidgetBase, MapRegion] = {}
        self.width = 0
        self.height = 0
        self.renders: dict[WidgetID, tuple[Region, Lines]] = {}
        self._cuts: list[list[int]] | None = None
        self.widgets: dict[WidgetID, WidgetBase] = {}

    def reset(self) -> None:
        self.renders.clear()
        self._cuts = None

    @abstractmethod
    def reflow(self, width: int, height: int) -> None:
        ...

    @property
    def map(self) -> dict[WidgetBase, MapRegion]:
        return self._layout_map

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

    @classmethod
    def _compare_lines(cls, lines1: Lines, lines2: Lines) -> Iterable[list[Segment]]:
        """Compares two renders and produce 'diff'"""
        delta_line: list[Segment] = [Control.home().segment]
        add_delta_segment = delta_line.append
        move_to_column = Control.move_to_column

        for y, (line1, line2) in enumerate(zip(lines1, lines2)):
            if line1 == line2:
                continue

            add_delta_segment(Control.move_to(0, y).segment)
            start_skip: int | None = None
            x1 = 0
            x2 = 0
            for segment1, segment2 in zip(line1, line2):
                if x1 == x2 and segment1 == segment2:
                    if start_skip is None:
                        start_skip = x1
                else:
                    if start_skip is not None:
                        add_delta_segment(move_to_column(x2).segment)
                        start_skip = None
                    add_delta_segment(segment2)
                x1 += segment1.cell_length
                x2 += segment2.cell_length

            if delta_line:
                yield delta_line[:]
                del delta_line[:]

    def _get_renders(self, console: Console) -> Iterable[tuple[Region, Lines]]:
        widgets = self.widgets
        width = self.width
        height = self.height
        screen_region = Region(0, 0, width, height)
        layout_map = self._layout_map

        widget_regions = sorted(
            ((widget, region, order) for widget, (region, order) in layout_map.items()),
            key=itemgetter(2),
            reverse=True,
        )

        @timer("render widget")
        def render(widget: WidgetBase, width: int, height: int) -> Lines:
            lines = console.render_lines(
                widget, console.options.update_dimensions(width, height)
            )
            return lines

        for widget, region, _order in widget_regions:
            region_lines = self.renders.get(widget.id)
            if region_lines is not None:
                yield region_lines
                continue

            lines = render(widget, region.width, region.height)
            if region in screen_region:
                self.renders[widget.id] = (region, lines)
                yield region, lines
            elif screen_region.overlaps(region):
                new_region = region.clip(width, height)
                delta_x = new_region.x - region.x
                delta_y = new_region.y - region.y
                region = new_region
                lines = lines[delta_y : delta_y + region.height]
                lines = [
                    list(Segment.divide(line, [delta_x, delta_x + region.width]))[1]
                    for line in lines
                ]
                self.renders[widget.id] = (region, lines)
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

    @timer("render")
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
        widgets = self.widgets
        width = self.width
        height = self.height
        screen = Region(0, 0, width, height)
        clip = clip or screen
        clip_x, clip_y, clip_x2, clip_y2 = clip.corners

        divide = Segment.divide
        back = Style.parse("on blue")

        # Maps each cut on to a list of segments
        cuts = self.cuts
        chops: list[dict[int, list[Segment] | None]] = [
            {cut: None for cut in cut_set} for cut_set in cuts
        ]

        # TODO: Provide an option to update the background
        background_render = [[Segment(" " * width, back)] for _ in range(height)]
        # Go through all the renders in reverse order and fill buckets with no render
        renders = self._get_renders(widgets, console)
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
                        _, *cut_segments = divide(
                            line, [cut - region.x for cut in final_cuts]
                        )
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

    def render_update(self, console: Console, widget: WidgetBase) -> LayoutUpdate:
        region, lines = self.renders[widget.id]
        new_lines = console.render_lines(
            widget, console.options.update_dimensions(region.width, region.height)
        )
        self.renders[widget.id] = (region, new_lines)

        update_lines = self.render(console, region).lines
        return LayoutUpdate(update_lines, region.x, region.y)
