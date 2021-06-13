from __future__ import annotations
import logging

import logging
import sys

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from rich.console import Console, ConsoleOptions, RenderableType
from rich.segment import Segment

from .. import events
from ..widget import Widget, Reactive
from ..geometry import Point, Dimensions
from ..scrollbar import VerticalBar

log = logging.getLogger("rich")

ScrollMethod = Literal["always", "never", "auto", "overlay"]


class Window(Widget):
    def __init__(
        self, renderable: RenderableType, y_scroll: ScrollMethod = "always"
    ) -> None:
        self.renderable = renderable
        self.y_scroll = y_scroll
        self._virtual_size: Dimensions | None = None
        self._renderable_updated = True
        self._lines: list[list[Segment]] = []
        super().__init__()

    position: Reactive[int] = Reactive(60)
    show_vertical_bar: Reactive[bool] = Reactive(True)

    @property
    def virtual_size(self) -> Dimensions:
        return self._virtual_size or self.size

    def require_repaint(self) -> None:
        del self._lines[:]
        return super().require_repaint()

    def get_lines(
        self, console: Console, options: ConsoleOptions
    ) -> list[list[Segment]]:
        if not self._lines:
            width = self.size.width
            if self.show_vertical_bar and self.y_scroll != "overlay":
                width -= 1
            self._lines = console.render_lines(
                self.renderable, options.update_width(width)
            )
        return self._lines

    def update(self, renderable: RenderableType) -> None:
        self.renderable = renderable
        del self._lines[:]

    def render(self, console: Console, options: ConsoleOptions) -> RenderableType:
        height = options.height or console.height
        lines = self.get_lines(console, options)

        return VerticalBar(
            lines[self.position : self.position + height],
            height,
            len(lines),
            self.position,
            overlay=self.y_scroll == "overlay",
        )

    async def on_key(self, event: events.Key) -> None:
        log.debug("window.on_key; %s", event)
        if event.key == "down":
            self.position += 1
        elif event.key == "up":
            self.position -= 1
        event.stop_propagation()
