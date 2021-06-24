from __future__ import annotations

import logging

from rich.console import Console, RenderableType
from rich.layout import Layout
from rich.style import StyleType
from rich.text import Text

from .. import events
from ..scrollbar import ScrollBar
from ..geometry import clamp
from ..page import Page
from ..view import LayoutView
from ..widget import Reactive, StaticWidget


log = logging.getLogger("rich")


class ScrollView(LayoutView):
    def __init__(
        self,
        renderable: RenderableType,
        name: str | None = None,
        style: StyleType = "",
        fluid: bool = True,
    ) -> None:
        self.fluid = fluid
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

    target_y: Reactive[float] = Reactive(0)

    def validate_y(self, value: float) -> float:
        return clamp(value, 0, self._page.contents_size.height - self.size.height)

    def validate_target_y(self, value: float) -> float:
        return clamp(value, 0, self._page.contents_size.height - self.size.height)

    def update_y(self, old_value: float, new_value: float) -> None:
        self._page.y = round(new_value)
        self._vertical_scrollbar.position = round(new_value)

    async def on_mount(self, event: events.Mount) -> None:
        await self.mount_all(
            content=self._page,
            vertical_scrollbar=self._vertical_scrollbar,
            # horizontal_scrollbar=self._horizontal_Scrollbar,
        )

    async def on_idle(self, event: events.Idle) -> None:
        self._vertical_scrollbar.virtual_size = self._page.virtual_size.height
        self._vertical_scrollbar.window_size = self.size.height
        await super().on_idle(event)

    async def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        self.target_y += 1.5
        self.animate("y", self.target_y, easing="out_cubic", speed=80)

    async def on_mouse_scroll_down(self, event: events.MouseScrollUp) -> None:
        self.target_y -= 1.5
        self.animate("y", self.target_y, easing="out_cubic", speed=80)

    async def on_key(self, event: events.Key) -> None:
        key = event.key
        if key == "down":
            self.target_y += 2
            self.animate("y", self.target_y, easing="linear", speed=100)
        elif key == "up":
            self.target_y -= 2
            self.animate("y", self.target_y, easing="linear", speed=100)
        elif key == "pagedown":
            self.target_y += self.size.height
            self.animate("y", self.target_y, easing="out_cubic")
        elif key == "pageup":
            self.target_y -= self.size.height
            self.animate("y", self.target_y, easing="out_cubic")

    async def on_resize(self, event: events.Resize) -> None:
        if self.fluid:
            self._page.update()
        await super().on_resize(event)
