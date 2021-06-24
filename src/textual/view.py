from __future__ import annotations

from abc import ABC, abstractmethod
from time import time
import logging
from typing import Optional, Tuple, TYPE_CHECKING

from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.layout import Layout
from rich.region import Region as LayoutRegion
import rich.repr
from rich.segment import Segments

from . import events
from ._context import active_app
from .geometry import Dimensions, Region
from .message import Message
from .message_pump import MessagePump
from .widget import StaticWidget, Widget, WidgetBase, UpdateMessage
from .widgets.header import Header

if TYPE_CHECKING:
    from .app import App

log = logging.getLogger("rich")


class NoWidget(Exception):
    pass


class View(ABC, WidgetBase):
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
    async def mount(
        self, widget: WidgetBase | RenderableType, *, slot: str = "main"
    ) -> None:
        ...

    async def mount_all(self, **widgets: WidgetBase) -> None:
        for slot, widget in widgets.items():
            await self.mount(widget, slot=slot)
        self.require_repaint()

    async def forward_event(self, event: events.Event) -> None:
        pass


@rich.repr.auto
class LayoutView(View):
    def __init__(self, layout: Layout = None, name: str | None = "default") -> None:
        self.name = name
        self.layout = layout or Layout()
        self.mouse_over: WidgetBase | None = None
        self.focused: WidgetBase | None = None
        self.size = Dimensions(0, 0)
        self._widgets: set[WidgetBase] = set()
        super().__init__(name)
        self.enable_messages(events.Idle)

    def __rich_repr__(self) -> rich.repr.RichReprResult:
        yield "name", self.name

    @property
    def is_root_view(self) -> bool:
        return self._parent is self.app

    # def check_repaint(self) -> bool:
    #     return True

    def render(self) -> RenderableType:
        return self.layout

    # def __rich__(self) -> Layout:
    #     return self.render()

    # def __rich_console__(
    #     self, console: Console, options: ConsoleOptions
    # ) -> RenderResult:
    #     width, height = self.size
    #     segments = console.render(self.layout, options.update_dimensions(width, height))
    #     yield from segments

    def get_widget_at(
        self, x: int, y: int, deep: bool = False
    ) -> Tuple[Widget, Region]:

        for layout, (layout_region, render) in self.layout.map.items():
            region = Region(*layout_region)
            if region.contains(x, y):
                widget = layout.renderable
                if deep and isinstance(layout.renderable, View):

                    view = layout.renderable
                    translate_x = region.x
                    translate_y = region.y
                    widget, region = view.get_widget_at(
                        x - region.x, y - region.y, deep=True
                    )
                    region = region.translate(translate_x, translate_y)

                if isinstance(widget, WidgetBase):
                    return widget, region

        raise NoWidget(f"No widget at {x}, {y}")

    async def on_message(self, message: Message) -> None:

        if isinstance(message, UpdateMessage):
            widget = message.widget
            # if widget in self._widgets:

            for layout, (region, render) in self.layout.map.items():
                if layout.renderable is message.sender:

                    if not isinstance(widget, WidgetBase):
                        continue

                    if self.is_root_view:
                        try:
                            update = widget.render_update(
                                region.x + message.offset_x, region.y + message.offset_y
                            )
                        except Exception:
                            log.exception("update error")
                            raise
                        self.console.print(Segments(update), end="")
                    else:
                        await self._parent.on_message(
                            UpdateMessage(
                                self,
                                widget,
                                offset_x=message.offset_x + region.x,
                                offset_y=message.offset_y + region.y,
                            )
                        )
                    break
            else:
                pass
                # log.warning("Update widget not found")

    # async def on_create(self, event: events.Created) -> None:
    #     await self.mount(Header(self.title))

    async def mount(
        self, widget: WidgetBase | RenderableType, *, slot: str = "main"
    ) -> None:
        if not isinstance(widget, WidgetBase):
            log.debug("MOUNTED %r", widget)
            widget = StaticWidget(widget)
        self.layout[slot].update(widget)
        await self.app.add(widget)
        widget.set_parent(self)
        await widget.post_message(events.Mount(sender=self))
        self._widgets.add(widget)

    async def layout_update(self) -> None:
        if not self.size:
            return
        width, height = self.size
        region_map = self.layout._make_region_map(width, height)
        for layout, region in region_map.items():
            if isinstance(layout.renderable, WidgetBase):
                await layout.renderable.post_message(
                    events.Resize(self, region.width, region.height)
                )
        self.app.refresh()
        # await self.repaint()

    async def on_resize(self, event: events.Resize) -> None:
        self.size = Dimensions(event.width, event.height)
        await self.layout_update()

    async def _on_mouse_move(self, event: events.MouseMove) -> None:
        try:
            widget, region = self.get_widget_at(event.x, event.y, deep=True)
        except NoWidget:
            await self.app.set_mouse_over(None)
        else:
            await self.app.set_mouse_over(widget)

            await widget.forward_event(
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

    async def forward_event(self, event: events.Event) -> None:

        if isinstance(event, (events.Enter, events.Leave)):
            await self.post_message(event)

        elif isinstance(event, events.MouseMove):
            await self._on_mouse_move(event)

        elif isinstance(event, events.MouseEvent):
            try:
                widget, region = self.get_widget_at(event.x, event.y, deep=True)
            except NoWidget:
                if isinstance(event, events.MouseDown):
                    await self.app.set_focus(None)
            else:
                if isinstance(event, events.MouseDown):
                    await self.app.set_focus(widget)
                await widget.forward_event(event.offset(-region.x, -region.y))

        elif isinstance(event, (events.MouseScrollDown, events.MouseScrollUp)):
            widget, _region = self.get_widget_at(event.x, event.y, deep=True)
            scroll_widget = widget or self.focused
            if scroll_widget is not None:
                await scroll_widget.forward_event(event)
        else:
            if self.focused is not None:
                await self.focused.forward_event(event)

    async def action_toggle(self, layout_name: str) -> None:
        visible = self.layout[layout_name].visible
        self.layout[layout_name].visible = not visible
        await self.layout_update()
