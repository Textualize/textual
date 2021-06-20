from __future__ import annotations

import logging

from typing import Iterable

from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.control import Control
from rich.segment import Segment


log = logging.getLogger("rich")


class LineCache:
    def __init__(self) -> None:
        self.lines: list[list[Segment]] = []
        self._dirty: list[bool] = []

    def update(
        self, console: Console, options: ConsoleOptions, renderable: RenderableType
    ) -> None:
        self.lines = console.render_lines(renderable, options, new_lines=True)
        self._dirty = [True] * len(self.lines)

    @property
    def dirty(self) -> bool:
        return any(self._dirty)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        for line in self.lines:
            yield from line

    def render(self, x: int, y: int) -> Iterable[Segment]:
        move_to = Control.move_to
        for offset_y, (line, dirty) in enumerate(zip(self.lines, self._dirty), y):
            if dirty:
                yield move_to(x, offset_y).segment
                yield from line

        self._dirty[:] = [False] * len(self.lines)
