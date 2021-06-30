from __future__ import annotations

from abc import ABC, abstractmethod, abstractmethod
from dataclasses import dataclass
from itertools import chain
from operator import itemgetter
from time import time
from typing import cast, Iterable, NamedTuple, TYPE_CHECKING

import rich.repr
from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.segment import Segment, SegmentLines
from rich.style import Style

from ._loop import loop_last
from ._profile import timer
from ._types import Lines

from .geometry import Region


if TYPE_CHECKING:
    from .widget import WidgetBase, WidgetID


class MapRegion(NamedTuple):
    region: Region
    order: tuple[int, int]


class Layout(ABC):
    """A class responsible for arranging widgets in a given area."""

    @abstractmethod
    def __call__(
        self, widgets: dict[WidgetID, WidgetBase], width: int, height: int
    ) -> LayoutMap:
        """Generate the layout.

        Args:
            width (int): width of enclosing area.
            height (int): height of enclosing area.

        Returns:
            dict[WidgetID, MapRegion]: Map of widget on to map region.
        """


class LayoutMap:
    """Responsible for rendering a layout."""

    def __init__(self, map: dict[WidgetID, MapRegion], width: int, height: int) -> None:
        """Responsible for rendering a layout

        Args:
            layout_map (dict[WidgetID, MapRegion]): A map of Widget ID on to a MapRegion.
            width (int): Width of layout.
            height (int): Height of layout.
        """
        self._layout_map = map
        self.width = width
        self.height = height

    def _get_renders(
        self, widgets: dict[WidgetID, WidgetBase], console: Console
    ) -> Iterable[tuple[Region, Lines]]:

        width = self.width
        height = self.height
        screen_region = Region(0, 0, width, height)
        layout_map = self._layout_map

        widget_regions = sorted(
            (
                (widgets[widget_id], region, order)
                for widget_id, (region, order) in layout_map.items()
            ),
            key=itemgetter(2),
            reverse=True,
        )

        def render(widget: WidgetBase, width: int, height: int) -> Lines:
            lines = console.render_lines(
                widget, console.options.update_dimensions(width, height)
            )
            return lines

        for widget, region, _order in widget_regions:
            lines = render(widget, region.width, region.height)
            if region in screen_region:
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
                yield region, lines

    def render(
        self,
        widgets: dict[WidgetID, WidgetBase],
        console: Console,
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
        _Segment = Segment
        divide = _Segment.divide
        back = Style.parse("on blue")
        cuts = [{0, width} for _ in range(height)]

        renders = list(self._get_renders(widgets, console))

        for region, lines in renders:
            borders = {region.x, region.x + region.width}
            for y, line in enumerate(lines, region.y):
                cuts[y].update(borders)

        buckets: list[dict[int, list[Segment] | None]] = [
            {cut: None for cut in cut_set} for cut_set in cuts
        ]

        ordered_cuts = [sorted(cut_set) for cut_set in cuts]

        screen_region = Region(0, 0, width, height)
        background_render = [[Segment(" " * width, back)] for _ in range(height)]

        for region, lines in chain(renders, [(screen_region, background_render)]):
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

        output_lines: list[list[Segment]] = []
        add_line = output_lines.append
        for bucket in buckets:
            render_line: list[Segment] = sum(
                (
                    cast(list, segments)
                    for _, segments in sorted(bucket.items())
                    if segments
                ),
                start=[],
            )
            add_line(render_line)
        return SegmentLines(output_lines, new_lines=True)
