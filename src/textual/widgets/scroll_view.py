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
        layout = Layout(name="outer")
        layout.split_row(
            Layout(name="content", ratio=1), Layout(name="vertical_scrollbar", size=1)
        )
        # layout["main"].split_column(
        #     Layout(name="content", ratio=1), Layout(name="horizontal_scrollbar", size=1)
        # )
        self._vertical_scrollbar = ScrollBar(vertical=True)
        # self._horizontal_Scrollbar = ScrollBar(vertical=False)
        self._page = Page(renderable, style=style)
        super().__init__(layout=layout, name=name)

    x: Reactive[float] = Reactive(0)
    y: Reactive[float] = Reactive(0)

    def validate_y(self, value: float) -> int:
        return max(0, value)

    def update_y(self, old_value: float, new_value: float) -> None:
        self._page.y = int(new_value)
        self._vertical_scrollbar.position = int(new_value)

    async def on_mount(self, event: events.Mount) -> None:
        await self.mount_all(
            content=self._page,
            vertical_scrollbar=self._vertical_scrollbar,
            # horizontal_scrollbar=self._horizontal_Scrollbar,
        )

    async def on_idle(self, event: events.Idle) -> None:
        self._vertical_scrollbar.virtual_size = self._page.virtual_size.height
        self._vertical_scrollbar.window_size = self.size.height
        # self._vertical_scrollbar.position = self.position_y
        await super().on_idle(event)

    async def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        self._vertical_scrollbar.position += 1

    async def on_mouse_scroll_down(self, event: events.MouseScrollUp) -> None:
        self._vertical_scrollbar.position -= 1

    async def on_key(self, event: events.Key) -> None:
        if event.key == "down":
            self.y += 1
        elif event.key == "up":
            self.y -= 1
        elif event.key == "pagedown":
            self._animator.animate("y", self.y + self.size.height, duration=0.5)
        elif event.key == "pageup":
            self._animator.animate("y", self.y - self.size.height, duration=0.5)
