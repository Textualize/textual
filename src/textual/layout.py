from __future__ import annotations

from abc import ABC, abstractmethod, abstractmethod
from dataclasses import dataclass
from typing import Iterable, TYPE_CHECKING

from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.segment import Segment, SegmentLines
from rich.style import Style

from ._loop import loop_last
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

    def render(self, console: Console, width: int, height: int) -> list[list[Segment]]:
        _Segment = Segment
        back = Style.parse("on blue")
        output_lines = [[_Segment(" " * width, back, None)] for _ in range(height)]

        for widget, (region, lines) in self.map.items():

            for y, line in enumerate(lines, region.y):
                output_line = output_lines[y]
                pre, _occluded, post = Segment.divide(
                    output_line, (region.x, region.limit.x)
                )
                output_line[:] = pre + line + post

        return output_lines

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

    v = Vertical((widget1, widget2), 5, 2)
    v.reflow(console, console.width, console.height)

    from rich import print

    print(v)
