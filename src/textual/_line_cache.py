from __future__ import annotations

import logging

from typing import Iterable

from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.control import Control
from rich.segment import Segment


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
        lines = console.render_lines(renderable, options, new_lines=True)
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

    def render(self, x: int, y: int) -> Iterable[Segment]:
        move_to = Control.move_to
        for offset_y, (line, dirty) in enumerate(zip(self.lines, self._dirty), y):
            if dirty:
                yield move_to(x, offset_y).segment
                yield from line
        self._dirty[:] = [False] * len(self.lines)
