from __future__ import annotations

from logging import getLogger

from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.padding import Padding, PaddingDimensions
from rich.segment import Segment
from rich.style import StyleType

from .geometry import Size, Offset
from .message import Message
from .widget import Widget, Reactive

log = getLogger("rich")


class PageUpdate(Message):
    def can_replace(self, message: "Message") -> bool:
        return isinstance(message, PageUpdate)


class PageRender:
    def __init__(
        self,
        page: Page,
        renderable: RenderableType,
        width: int | None = None,
        height: int | None = None,
        style: StyleType = "",
        padding: PaddingDimensions = (0, 0),
    ) -> None:
        self.page = page
        self.renderable = renderable
        self.width = width
        self.height = height
        self.style = style
        self.padding = padding
        self.offset = Offset(0, 0)
        self._render_width: int | None = None
        self._render_height: int | None = None
        self.size = Size(0, 0)
        self._lines: list[list[Segment]] = []

    def move_to(self, x: int = 0, y: int = 0) -> None:
        self.offset = Offset(x, y)

    def clear(self) -> None:
        self._render_width = None
        self._render_height = None
        del self._lines[:]

    def update(self, renderable: RenderableType) -> None:
        self.renderable = renderable
        self.clear()

    def render(self, console: Console, options: ConsoleOptions) -> None:
        width = self.width or options.max_width or console.width
        options = options.update_dimensions(width, None)
        style = console.get_style(self.style)
        renderable = self.renderable
        if self.padding:
            renderable = Padding(renderable, self.padding)
        self._lines[:] = console.render_lines(renderable, options, style=style)
        self.size = Size(width, len(self._lines))
        self.page.emit_no_wait(PageUpdate(self.page))

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

        if x:

            def width_view(line: list[Segment]) -> list[Segment]:
                _, line = Segment.divide(line, [x, x + width])
                return line

            window_lines = [width_view(line) for line in window_lines]

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
        self, renderable: RenderableType, name: str | None = None, style: StyleType = ""
    ):
        self._page = PageRender(self, renderable, style=style)
        super().__init__(name=name)

    scroll_x: Reactive[int] = Reactive(0)
    scroll_y: Reactive[int] = Reactive(0)

    def validate_scroll_x(self, value: int) -> int:
        return max(0, value)

    def validate_scroll_y(self, value: int) -> int:
        return max(0, value)

    async def watch_scroll_x(self, new: int) -> None:
        x, y = self._page.offset
        self._page.offset = Offset(new, y)

    async def watch_scroll_y(self, new: int) -> None:
        x, y = self._page.offset
        self._page.offset = Offset(x, new)

    def update(self, renderable: RenderableType | None = None) -> None:
        if renderable:
            self._page.update(renderable)
        else:
            self._page.clear()
        self.require_repaint()

    @property
    def virtual_size(self) -> Size:
        return self._page.size

    def render(self) -> RenderableType:
        return self._page
