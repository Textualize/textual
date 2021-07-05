from __future__ import annotations

from typing import Iterable

from rich.console import Console, RenderableType
from rich.control import Control
from rich.segment import Segment, Segments

from .geometry import Point
from ._loop import loop_last


class ScreenUpdate:
    def __init__(
        self, console: Console, renderable: RenderableType, width: int, height: int
    ) -> None:

        self.lines = console.render_lines(
            renderable, console.options.update_dimensions(width, height)
        )
        self.offset = Point(0, 0)

    def render(self, x: int, y: int) -> Iterable[Segment]:
        move_to = Control.move_to
        new_line = Segment.line()
        for last, (offset_y, line) in loop_last(enumerate(self.lines, y)):
            yield move_to(x, offset_y).segment
            yield from line
            if not last:
                yield new_line

    def __rich__(self) -> RenderableType:
        x, y = self.offset
        update = self.render(x, y)
        return Segments(update)
