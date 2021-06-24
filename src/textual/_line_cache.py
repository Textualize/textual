from __future__ import annotations


import logging

from typing import Iterable

from rich.cells import cell_len
from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.control import Control
from rich.segment import Segment
from rich.style import Style

from ._loop import loop_last

log = logging.getLogger("rich")


class LineCache:
    def __init__(self, lines: list[list[Segment]]) -> None:
        self.lines = lines
        self._dirty = [True] * len(self.lines)

    @classmethod
    def from_renderable(
        cls,
        console: Console,
        renderable: RenderableType,
        width: int,
        height: int,
    ) -> "LineCache":
        options = console.options.update_dimensions(width, height)
        lines = console.render_lines(renderable, options)
        return cls(lines)

    @property
    def dirty(self) -> bool:
        return any(self._dirty)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:

        new_line = Segment.line()
        for line in self.lines:
            yield from line
            yield new_line

    def render(self, x: int, y: int, width: int, height: int) -> Iterable[Segment]:
        move_to = Control.move_to
        lines = self.lines[:height]
        new_line = Segment.line()
        for last, (offset_y, (line, dirty)) in loop_last(
            enumerate(zip(lines, self._dirty), y)
        ):
            if dirty:
                yield move_to(x, offset_y).segment
                yield from Segment.adjust_line_length(line, width)
                if not last:
                    yield new_line
        self._dirty[:] = [False] * len(self.lines)

    def get_style_at(self, x: int, y: int) -> Style:
        try:
            line = self.lines[y]
        except IndexError:
            return Style.null()
        end = 0
        for segment in line:
            end += cell_len(segment.text)
            if x < end:
                return segment.style or Style.null()
        return Style.null()
