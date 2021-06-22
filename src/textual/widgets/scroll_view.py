from __future__ import annotations

import logging

from rich.console import Console, RenderableType
from rich.layout import Layout
from rich.style import StyleType
from rich.text import Text

from .. import events
from ..scrollbar import ScrollBar

from ..page import Page
from ..view import LayoutView
from ..widget import Reactive, StaticWidget


log = logging.getLogger("rich")


class ScrollView(LayoutView):
    def __init__(
        self, renderable: RenderableType, name: str | None = None, style: StyleType = ""
    ) -> None:
        layout = Layout()
        layout.split_row(
            Layout(name="main", ratio=1), Layout(name="vertical_scrollbar", size=1)
        )
        layout["main"].split_column(
            Layout(name="content", ratio=1), Layout(name="horizontal_scrollbar", size=1)
        )
        self._vertical_scrollbar = ScrollBar(vertical=True)
        self._horizontal_Scrollbar = ScrollBar(vertical=False)
        self._page = Page(renderable, style=style)
        super().__init__(layout=layout, name=name)

    position_x: Reactive[int] = Reactive(0)
    position_y: Reactive[int] = Reactive(0)

    def validate_position_y(self, value: int) -> int:
        return max(0, value)

    def update_position_y(self, old_value: int, new_value: int) -> None:
        self._vertical_scrollbar.position = new_value

    async def on_mount(self, event: events.Mount) -> None:
        await self.mount_all(
            content=self._page,
            vertical_scrollbar=self._vertical_scrollbar,
            horizontal_scrollbar=self._horizontal_Scrollbar,
        )

    async def on_idle(self, event: events.Idle) -> None:
        self._vertical_scrollbar.virtual_size = self._page.virtual_size.height
        self._vertical_scrollbar.window_size = self.size.height
        # self._vertical_scrollbar.position = self.position_y
        log.debug("SCROLLVIEW BAR %r", self._vertical_scrollbar)
        log.debug("SCROLL SIZE %r", self._page.size)
        await super().on_idle(event)

    async def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        self._vertical_scrollbar.position += 1

    async def on_mouse_scroll_down(self, event: events.MouseScrollUp) -> None:
        self._vertical_scrollbar.position -= 1

    async def on_key(self, event: events.Key) -> None:
        if event.key == "down":
            self.position_y += 1
        elif event.key == "up":
            self.position_y -= 1
        # self._vertical_scrollbar.require_repaint()
        # await self._vertical_scrollbar.post_message(events.Null(self))
        # self.require_repaint()