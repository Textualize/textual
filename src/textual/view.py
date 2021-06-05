from abc import ABC, abstractmethod
import logging
from typing import Optional, Set, Tuple, TYPE_CHECKING

from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.layout import Layout
from rich.region import Region
from rich.repr import rich_repr, RichReprResult

from . import events
from ._context import active_app
from .message import Message
from .message_pump import MessagePump
from .widget import Widget
from .widgets.header import Header

if TYPE_CHECKING:
    from .app import App

log = logging.getLogger("rich")


class NoWidget(Exception):
    pass


@rich_repr
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

    def __rich_repr__(self) -> RichReprResult:
        return
        yield

    @abstractmethod
    async def mount(self, widget: Widget, *, slot: str = "main") -> None:
        ...

    async def mount_all(self, **widgets: Widget) -> None:
        for slot, widget in widgets.items():
            await self.mount(widget, slot=slot)


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
        self.mouse_over: Optional[MessagePump] = None
        self.focused: Optional[MessagePump] = None
        self._widgets: Set[Widget] = set()
        super().__init__()
        self.enable_messages(events.Idle)

    def __rich_repr__(self) -> RichReprResult:
        yield "name", self.name

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        segments = console.render(self.layout, options)
        yield from segments

    def get_widget_at(self, x: int, y: int) -> Tuple[Widget, Region]:
        for layout, (region, render) in self.layout.map.items():
            if region.contains(x, y):
                if isinstance(layout.renderable, Widget):
                    return layout.renderable, region
                else:
                    break
        raise NoWidget(f"No widget at ${x}, ${y}")

    async def on_create(self, event: events.Created) -> None:
        await self.mount(Header(self.title))

    async def mount(self, widget: Widget, *, slot: str = "main") -> None:
        self.layout[slot].update(widget)
        await self.app.add(widget)
        await widget.post_message(events.Mount(sender=self))
        self._widgets.add(widget)

    async def set_focus(self, widget: Optional[Widget]) -> None:
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

    async def on_startup(self, event: events.Startup) -> None:
        await self.mount(Header(self.title), slot="header")

    async def on_resize(self, event: events.Resize) -> None:
        region_map = self.layout._make_region_map(event.width, event.height)
        for layout, region in region_map.items():
            if isinstance(layout.renderable, Widget):
                await layout.renderable.post_message(
                    events.Resize(self, region.width, region.height)
                )
        self.app.refresh()

    async def on_move(self, event: events.Move) -> None:
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
                events.Move(self, event.x - region.x, event.y - region.y)
            )

    async def on_click(self, event: events.Click) -> None:
        try:
            widget, _region = self.get_widget_at(event.x, event.y)
        except NoWidget:
            await self.set_focus(None)
        else:
            await self.set_focus(widget)
