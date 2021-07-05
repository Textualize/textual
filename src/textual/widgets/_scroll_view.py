from __future__ import annotations

import logging

from rich.console import RenderableType
from rich.style import StyleType


from .. import events
from ..message import Message
from ..scrollbar import ScrollBar, ScrollDown, ScrollUp
from ..geometry import clamp
from ..page import Page
from ..view import DockView
from ..reactive import Reactive


log = logging.getLogger("rich")


class ScrollView(DockView):
    def __init__(
        self,
        renderable: RenderableType,
        *,
        name: str | None = None,
        style: StyleType = "",
        fluid: bool = True,
    ) -> None:
        self.fluid = fluid
        self._vertical_scrollbar = ScrollBar(vertical=True)
        self._page = Page(renderable, style=style)
        super().__init__(name="ScrollView")

    x: Reactive[float] = Reactive(0)
    y: Reactive[float] = Reactive(0)

    target_y: Reactive[float] = Reactive(0)

    def validate_y(self, value: float) -> float:
        return clamp(value, 0, self._page.contents_size.height - self.size.height)

    def validate_target_y(self, value: float) -> float:
        return clamp(value, 0, self._page.contents_size.height - self.size.height)

    def watch_y(self, new_value: float) -> None:
        self._page.y = round(new_value)
        self._vertical_scrollbar.position = round(new_value)

    async def on_mount(self, event: events.Mount) -> None:
        await self.dock(self._vertical_scrollbar, edge="right", size=1)
        await self.dock(self._page, edge="top")

    async def on_idle(self, event: events.Idle) -> None:
        self._vertical_scrollbar.virtual_size = self._page.virtual_size.height
        self._vertical_scrollbar.window_size = self.size.height

        await super().on_idle(event)

    async def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        self.scroll_up()

    async def on_mouse_scroll_down(self, event: events.MouseScrollUp) -> None:
        self.scroll_down()

    def scroll_up(self) -> None:
        self.target_y += 1.5
        self.animate("y", self.target_y, easing="out_cubic", speed=80)

    def scroll_down(self) -> None:
        self.target_y -= 1.5
        self.animate("y", self.target_y, easing="out_cubic", speed=80)

    def page_up(self) -> None:
        self.target_y -= self.size.height
        self.animate("y", self.target_y, easing="out_cubic")

    def page_down(self) -> None:
        self.target_y += self.size.height
        self.animate("y", self.target_y, easing="out_cubic")

    async def on_key(self, event: events.Key) -> None:
        key = event.key
        if key == "down":
            self.target_y += 2
            self.animate("y", self.target_y, easing="linear", speed=100)
        elif key == "up":
            self.target_y -= 2
            self.animate("y", self.target_y, easing="linear", speed=100)
        elif key == "pagedown":
            log.debug("%r", self.size)
            self.target_y += self.size.height
            self.animate("y", self.target_y, easing="out_cubic")
        elif key == "pageup":
            log.debug("%r", self.size)
            self.target_y -= self.size.height
            self.animate("y", self.target_y, easing="out_cubic")

    async def on_resize(self, event: events.Resize) -> None:
        if self.fluid:
            self._page.update()
        await super().on_resize(event)

    async def on_message(self, message: Message) -> None:
        if isinstance(message, ScrollUp):
            self.page_up()
        elif isinstance(message, ScrollDown):
            self.page_down()
        else:
            await super().on_message(message)
