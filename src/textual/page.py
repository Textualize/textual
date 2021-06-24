from __future__ import annotations

from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.padding import Padding, PaddingDimensions
from rich.segment import Segment
from rich.style import StyleType

from .geometry import Dimensions, Point
from .widget import Widget, Reactive


class PageRender:
    def __init__(
        self,
        renderable: RenderableType,
        width: int | None = None,
        height: int | None = None,
        style: StyleType = "",
        padding: PaddingDimensions = 1,
    ) -> None:
        self.renderable = renderable
        self.width = width
        self.height = height
        self.style = style
        self.padding = padding
        self.offset = Point(0, 0)
        self._render_width: int | None = None
        self._render_height: int | None = None
        self.size = Dimensions(0, 0)
        self._lines: list[list[Segment]] = []

    def move_to(self, x: int = 0, y: int = 0) -> None:
        self.offset = Point(x, y)

    def clear(self) -> None:
        self._render_width = None
        self._render_height = None
        del self._lines[:]

    def update(self, renderable: RenderableType) -> None:
        self.renderable = renderable
        self.clear()

    def render(self, console: Console, options: ConsoleOptions) -> None:
        width = self.width or options.max_width or console.width
        height = self.height or options.height or None
        options = options.update_dimensions(width, None)
        style = console.get_style(self.style)
        renderable = self.renderable
        if self.padding:
            renderable = Padding(renderable, self.padding)
        self._lines[:] = console.render_lines(renderable, options, style=style)
        self.size = Dimensions(width, len(self._lines))

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

        new_line = Segment.line()
        for line in window_lines:
            yield from line
            yield new_line


class Page(Widget):
    def __init__(
        self, renderable: RenderableType, name: str = None, style: StyleType = ""
    ):
        self._page = PageRender(renderable, style=style)
        super().__init__(name=name)

    x: Reactive[int] = Reactive(0)
    y: Reactive[int] = Reactive(0)

    @property
    def contents_size(self) -> Dimensions:
        return self._page.size

    def validate_y(self, value: int) -> int:
        return max(0, value)

    def update_y(self, old: int, new: int) -> None:
        x, y = self._page.offset
        self._page.offset = Point(x, new)

    def update(self, renderable: RenderableType | None = None) -> None:

        if renderable:
            self._page.update(renderable)
        else:
            self._page.clear()

    @property
    def virtual_size(self) -> Dimensions:
        return self._page.size

    def render(self) -> RenderableType:
        return self._page
