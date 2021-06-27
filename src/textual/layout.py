from __future__ import annotations

from abc import ABC, abstractmethod, abstractmethod
from dataclasses import dataclass
from itertools import chain
from time import time
from typing import cast, Iterable, TYPE_CHECKING

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


if TYPE_CHECKING:
    from .widget import Widget, WidgetBase

    LayoutMap = dict[WidgetBase, tuple[Region, Lines]]


class LayoutBase(ABC):
    def __init__(self, widgets: Iterable[Widget]) -> None:
        self._widgets = list(widgets)
        self.map: LayoutMap = {}
        self.window: Region = Region(0, 0, 0, 0)

    @abstractmethod
    def reflow(self, console: Console, width: int, height: int) -> None:
        ...

    # @timer("render")
    # def render(self, console: Console, width: int, height: int) -> list[list[Segment]]:

    #     _Segment = Segment
    #     back = Style.parse("on blue")
    #     output_lines = [[_Segment(" " * width, back, None)] for _ in range(height)]
    #     divide = _Segment.divide
    #     simplify = _Segment.simplify
    #     for widget, (region, lines) in self.map.items():

    #         for y, line in enumerate(lines, region.y):
    #             try:
    #                 output_line = output_lines[y]
    #             except IndexError:
    #                 break
    #             pre, _occluded, post = divide(
    #                 output_line, (region.x, region.x + region.width, width)
    #             )
    #             output_line[:] = chain(pre, line, post)

    #     return output_lines

    @timer("render")
    def render(
        self, console: Console, width: int, height: int
    ) -> Iterable[list[Segment]]:

        _Segment = Segment
        divide = _Segment.divide
        back = Style.parse("on blue")
        cuts = [{0, width} for _ in range(height)]
        for region, lines in self.map.values():
            borders = {region.x, region.x + region.width}
            for y, line in enumerate(lines, region.y):
                cuts[y].update(borders)

        buckets: list[dict[int, list[Segment] | None]] = [
            {cut: None for cut in cut_set} for cut_set in cuts
        ]

        ordered_cuts = [sorted(cut_set) for cut_set in cuts]

        screen_region = Region(0, 0, width, height)
        background_render = [[Segment(" " * width, back)] for _ in range(height)]

        for region, lines in chain(
            reversed(self.map.values()), [(screen_region, background_render)]
        ):
            for y, line in enumerate(lines, region.y):
                first_cut = region.x
                last_cut = region.x + region.width
                cuts = [
                    cut for cut in ordered_cuts[y] if (last_cut >= cut >= first_cut)
                ]

                _, *cut_segments = divide(line, [cut - region.x for cut in cuts])
                for cut, segments in zip(cuts, cut_segments):
                    if buckets[y][cut] is None:
                        buckets[y][cut] = segments

        for bucket in buckets:
            render_line: list[Segment] = sum(
                (
                    cast(list, segments)
                    for cut, segments in sorted(bucket.items())
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
    def __init__(
        self, widgets: Iterable[WidgetBase], gutter: int = 0, padding: int = 0
    ) -> None:
        self.gutter = gutter
        self.padding = padding
        super().__init__(widgets)

    @property
    def widgets(self) -> list[WidgetBase]:
        return self._widgets

    @timer("reflow")
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
            map[widget] = (region, lines)
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

    v = Vertical([Placeholder() for _ in range(10)], 3, -1)
    v.reflow(console, console.width, console.height)

    from rich import print

    print(v)
