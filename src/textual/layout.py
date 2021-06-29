from __future__ import annotations

from abc import ABC, abstractmethod, abstractmethod
from dataclasses import dataclass
from itertools import chain
from operator import attrgetter
from time import time
from typing import cast, Iterable, NamedTuple, TYPE_CHECKING

import rich.repr
from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.segment import Segment, SegmentLines
from rich.style import Style

from ._loop import loop_last
from ._profile import timer
from ._types import Lines

from .geometry import Point, Region


@dataclass
class LayoutOptions:
    """Basic options for layout."""

    name: str = ""
    order: int = 0
    z: int = 0
    offset_x: int = 0
    offset_y: int = 0


class RegionRender(NamedTuple):
    region: Region
    lines: Lines
    order: tuple[int, int]


if TYPE_CHECKING:
    from .widget import Widget, WidgetBase

    LayoutMap = dict[WidgetBase, RegionRender]


class LayoutBase(ABC):
    def __init__(self) -> None:
        self._widgets: list[WidgetBase] = []
        self.map: LayoutMap = {}

    @property
    def widgets(self) -> list[WidgetBase]:
        return self._widgets

    def _get_renders(self, width: int, height: int) -> Iterable[RegionRender]:
        screen_region = Region(0, 0, width, height)
        renders = sorted(self.map.values(), key=attrgetter("order"), reverse=True)
        for region_render in renders:
            if region_render.region in screen_region:
                yield region_render
            elif screen_region.overlaps(region_render.region):
                region, lines, order = region_render
                new_region = region.clip(width, height)
                delta_x = new_region.x - region.x
                delta_y = new_region.y - region.y
                region = new_region
                lines = lines[delta_y : delta_y + region.height]
                lines = [
                    list(Segment.divide(line, [delta_x, delta_x + region.width]))[1]
                    for line in lines
                ]
                yield RegionRender(region, lines, order)

    @abstractmethod
    def reflow(self, console: Console, width: int, height: int) -> None:
        ...

    @timer("render")
    def render(
        self, console: Console, width: int, height: int
    ) -> Iterable[list[Segment]]:

        _Segment = Segment
        divide = _Segment.divide
        back = Style.parse("on blue")
        cuts = [{0, width} for _ in range(height)]

        renders = list(self._get_renders(width, height))
        for region, lines, _order in renders:
            borders = {region.x, region.x + region.width}
            for y, line in enumerate(lines, region.y):
                cuts[y].update(borders)

        buckets: list[dict[int, list[Segment] | None]] = [
            {cut: None for cut in cut_set} for cut_set in cuts
        ]

        ordered_cuts = [sorted(cut_set) for cut_set in cuts]

        screen_region = Region(0, 0, width, height)
        background_render = [[Segment(" " * width, back)] for _ in range(height)]

        for region, lines, _ in chain(
            renders, [(screen_region, background_render, (0, 0))]
        ):
            for y, line in enumerate(lines, region.y):
                first_cut = region.x
                last_cut = region.x + region.width
                final_cuts = [
                    cut for cut in ordered_cuts[y] if (last_cut >= cut >= first_cut)
                ]
                _, *cut_segments = divide(line, [cut - region.x for cut in final_cuts])
                for cut, segments in zip(final_cuts, cut_segments):
                    if buckets[y][cut] is None:
                        buckets[y][cut] = segments

        for bucket in buckets:
            render_line: list[Segment] = sum(
                (
                    cast(list, segments)
                    for _, segments in sorted(bucket.items())
                    if segments
                ),
                start=[],
            )
            yield render_line

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        lines = self.render(console, console.width, console.height)
        yield SegmentLines(lines, new_lines=True)


class Vertical(LayoutBase):
    def __init__(self, gutter: int = 0, padding: int = 0) -> None:
        self.gutter = gutter
        self.padding = padding
        super().__init__()

    @property
    def widgets(self) -> list[WidgetBase]:
        return self._widgets

    def reflow(self, console: Console, width: int, height: int) -> None:
        self.map.clear()
        y = self.gutter
        render_width = width - self.gutter * 2
        options = console.options
        map = self.map
        padding = self.padding
        for last, widget in loop_last(self.widgets):
            lines = console.render_lines(widget, options.update_width(render_width))
            region = Region(self.gutter, y, render_width, len(lines))
            map[widget] = RegionRender(region, lines, (0, 0))
            y += len(lines)
            if not last:
                y += padding


if __name__ == "__main__":

    from .widgets.placeholder import Placeholder
    from .widget import StaticWidget
    from rich.panel import Panel

    widget1 = Placeholder()
    widget2 = Placeholder()

    from rich.console import Console

    console = Console()

    v = Vertical(3, 2)
    v.widgets[:] = [Placeholder() for _ in range(10)]
    v.reflow(console, console.width, console.height)

    from rich import print

    print(v)
