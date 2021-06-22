from __future__ import annotations

from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.segment import Segment
from rich.style import StyleType

from .geometry import Point
from .widget import Widget


class Page:
    def __init__(
        self,
        renderable: RenderableType,
        width: int | None = None,
        height: int | None = None,
        style: StyleType = "",
    ) -> None:
        self.renderable = renderable
        self.width = width
        self.height = height
        self.style = style
        self.offset = Point(0, 0)
        self._render_width: int | None = None
        self._render_height: int | None = None
        self._lines: list[list[Segment]] = []

    def move_to(self, x: int = 0, y: int = 0) -> None:
        self.offset = Point(x, y)

    def refresh(self) -> None:
        self._render_width = None
        self._render_height = None
        del self._lines[:]

    def update(self, renderable: RenderableType) -> None:
        self.renderable = renderable
        self.refresh()

    def render(self, console: Console, options: ConsoleOptions) -> None:
        width = self._render_width = self.width or options.max_width or console.width
        height = self._render_height = self.height or options.height or None
        options = options.update_width(width)
        style = console.get_style(self.style)
        self._lines = console.render_lines(self.renderable, options, style=style)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        if not self._lines:
            self.render(console, options)
        style = console.get_style(self.style)
        width = self._render_width or console.width
        height = options.height or console.height
        x, y = self.offset
        window_lines = self._lines[y : y + height]

        missing_lines = len(window_lines) - height
        if missing_lines:
            blank_line = [Segment(" " * width, style), Segment.line()]
            window_lines.extend(blank_line for _ in range(missing_lines))

        for line in window_lines:
            yield from line