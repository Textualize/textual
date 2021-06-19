from __future__ import annotations

from abc import ABC, abstractmethod
from time import time
import logging
from typing import Optional, Tuple, TYPE_CHECKING

from rich.console import Console, ConsoleOptions, RenderResult
from rich.layout import Layout
from rich.region import Region as LayoutRegion
from rich.repr import rich_repr, RichReprResult
from rich.segment import Segments

from . import events
from ._context import active_app
from .geometry import Dimensions, Region
from .message import Message
from .message_pump import MessagePump
from .widget import Widget, UpdateMessage
from .widgets.header import Header

if TYPE_CHECKING:
    from .app import App

log = logging.getLogger("rich")


class NoWidget(Exception):
    pass


class View(ABC, MessagePump):
    @property
    def app(self) -> "App":
        return active_app.get()

    @property
    def console(self) -> Console:
        return active_app.get().console

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        return
        yield

    @abstractmethod
    async def mount(self, widget: Widget, *, slot: str = "main") -> None:
        ...

    async def mount_all(self, **widgets: Widget) -> None:
        for slot, widget in widgets.items():
            await self.mount(widget, slot=slot)

    async def forward_input_event(self, event: events.Event) -> None:
        pass


@rich_repr
class LayoutView(View):
    layout: Layout

    def __init__(
        self,
        layout: Layout = None,
        name: str = "default",
        title: str = "Layout Application",
    ) -> None:
        self.name = name
        self.title = title
        if layout is None:
            layout = Layout()
            layout.split_column(
                Layout(name="header", size=3, ratio=0),
                Layout(name="main", ratio=1),
                Layout(name="footer", size=1, ratio=0),
            )
            layout["main"].split_row(
                Layout(name="left", size=30, visible=True),
                Layout(name="body", ratio=1),
                Layout(name="right", size=30, visible=False),
            )
        self.layout = layout
        self.mouse_over: MessagePump | None = None
        self.focused: Widget | None = None
        self.size = Dimensions(0, 0)
        self._widgets: set[Widget] = set()
        super().__init__()
        self.enable_messages(events.Idle)

    def __rich_repr__(self) -> RichReprResult:
        yield "name", self.name

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        width, height = self.size
        segments = console.render(self.layout, options.update_dimensions(width, height))
        yield from segments

    def get_widget_at(self, x: int, y: int) -> Tuple[Widget, LayoutRegion]:
        for layout, (region, render) in self.layout.map.items():
            if Region(*region).contains(x, y):
                if isinstance(layout.renderable, Widget):
                    return layout.renderable, region
                else:
                    break
        raise NoWidget(f"No widget at ${x}, ${y}")

    async def on_message(self, message: Message) -> None:
        if isinstance(message, UpdateMessage):
            widget = message.sender
            if widget in self._widgets:
                for layout, (region, render) in self.layout.map.items():
                    if layout.renderable is widget:
                        assert isinstance(widget, Widget)
                        update = widget.render_update(region.x, region.y)
                        segments = Segments(update)
                        self.console.print(segments, end="")

    # async def on_create(self, event: events.Created) -> None:
    #     await self.mount(Header(self.title))

    async def mount(self, widget: Widget, *, slot: str = "main") -> None:
        self.layout[slot].update(widget)
        await self.app.add(widget)
        widget.set_parent(self)
        await widget.post_message(events.Mount(sender=self))
        self._widgets.add(widget)

    async def set_focus(self, widget: Optional[Widget]) -> None:
        log.debug("set_focus %r", widget)
        if widget == self.focused:
            return

        if widget is None:
            if self.focused is not None:
                focused = self.focused
                self.focused = None
                await focused.post_message(events.Blur(self))
        elif widget.can_focus:
            if self.focused is not None:
                await self.focused.post_message(events.Blur(self))
            if widget is not None and self.focused != widget:
                self.focused = widget
                await widget.post_message(events.Focus(self))

    # async def on_startup(self, event: events.Startup) -> None:
    #     await self.mount(Header(self.title), slot="header")

    async def layout_update(self) -> None:
        if not self.size:
            return
        width, height = self.size
        region_map = self.layout._make_region_map(width, height)
        for layout, region in region_map.items():
            if isinstance(layout.renderable, Widget):
                await layout.renderable.post_message(
                    events.Resize(self, region.width, region.height)
                )
        self.app.refresh()

    async def on_resize(self, event: events.Resize) -> None:
        self.size = Dimensions(event.width, event.height)
        await self.layout_update()

    async def _on_mouse_move(self, event: events.MouseMove) -> None:
        try:
            widget, region = self.get_widget_at(event.x, event.y)
        except NoWidget:
            if self.mouse_over is not None:
                try:
                    await self.mouse_over.post_message(events.Leave(self))
                finally:
                    self.mouse_over = None
        else:
            if self.mouse_over != widget:
                try:
                    if self.mouse_over is not None:
                        await self.mouse_over.post_message(events.Leave(self))
                    if widget is not None:
                        await widget.post_message(
                            events.Enter(self, event.x - region.x, event.y - region.y)
                        )
                finally:
                    self.mouse_over = widget
            await widget.post_message(
                events.MouseMove(
                    self,
                    event.x - region.x,
                    event.y - region.y,
                    event.button,
                    event.shift,
                    event.meta,
                    event.ctrl,
                )
            )

    async def forward_input_event(self, event: events.Event) -> None:
        if isinstance(event, (events.MouseDown)):
            try:
                widget, _region = self.get_widget_at(event.x, event.y)
            except NoWidget:
                await self.set_focus(None)
            else:
                await self.set_focus(widget)

        elif isinstance(event, events.MouseMove):
            await self._on_mouse_move(event)

        elif isinstance(event, events.MouseEvent):
            try:
                widget, region = self.get_widget_at(event.x, event.y)
            except NoWidget:
                pass
            else:
                await widget.forward_input_event(event)
        elif isinstance(event, (events.MouseScrollDown, events.MouseScrollUp)):
            widget, _region = self.get_widget_at(event.x, event.y)
            scroll_widget = widget or self.focused
            if scroll_widget is not None:
                await scroll_widget.forward_input_event(event)
        else:
            if self.focused is not None:
                await self.focused.forward_input_event(event)

    async def action_toggle(self, layout_name: str) -> None:
        visible = self.layout[layout_name].visible
        self.layout[layout_name].visible = not visible
        await self.layout_update()
