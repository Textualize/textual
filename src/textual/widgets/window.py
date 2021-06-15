from __future__ import annotations
import logging

import logging
import sys

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from rich.console import Console, ConsoleOptions, RenderableType
from rich.padding import Padding
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
        self._virtual_size: Dimensions = Dimensions(0, 0)
        self._renderable_updated = True
        self._lines: list[list[Segment]] = []
        super().__init__()

    def _validate_position(self, position: float) -> float:
        _position = position
        validated_pos = min(
            max(0, position), self._virtual_size.height - self.size.height
        )
        log.debug("virtual_size=%r size=%r", self._virtual_size, self.size)
        log.debug("%r %r", _position, validated_pos)
        return validated_pos

    position: Reactive[float] = Reactive(60, validator=_validate_position)
    show_vertical_bar: Reactive[bool] = Reactive(True)

    @property
    def virtual_size(self) -> Dimensions:
        return self._virtual_size or self.size

    def get_lines(
        self, console: Console, options: ConsoleOptions
    ) -> list[list[Segment]]:
        if not self._lines:
            width = self.size.width
            if self.show_vertical_bar and self.y_scroll != "overlay":
                width -= 1
            self._lines = console.render_lines(
                Padding(self.renderable, 1), options.update_width(width)
            )
            self._virtual_size = Dimensions(0, len(self._lines))
        return self._lines

    def update(self, renderable: RenderableType) -> None:
        self.renderable = renderable
        del self._lines[:]

    def render(self, console: Console, options: ConsoleOptions) -> RenderableType:
        height = self.size.height
        lines = self.get_lines(console, options)
        position = int(self.position)
        log.debug("%r, %r, %r", height, self._virtual_size, self.position)
        return VerticalBar(
            lines[position : position + height],
            height,
            self._virtual_size.height,
            self.position,
            overlay=self.y_scroll == "overlay",
        )

    async def on_key(self, event: events.Key) -> None:
        if event.key == "down":
            self.position += 1
        elif event.key == "up":
            self.position -= 1

    async def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        self.position += 1

    async def on_mouse_scroll_down(self, event: events.MouseScrollUp) -> None:
        self.position -= 1

    async def on_resize(self, event: events.Resize) -> None:
        del self._lines[:]
        self.position = self.position
        self.require_repaint()