from __future__ import annotations

from abc import ABC, abstractmethod
from itertools import chain
from time import time
import logging
from typing import cast, Iterable, Optional, Tuple, TYPE_CHECKING

from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.region import Region as LayoutRegion
import rich.repr
from rich.segment import Segments

from . import events
from ._context import active_app
from .layout import Layout, NoWidget
from .layouts.dock import DockEdge, DockLayout, Dock
from .geometry import Dimensions, Region
from .messages import UpdateMessage, LayoutMessage

from .widget import StaticWidget, Widget, WidgetID, Widget
from .widgets.header import Header

if TYPE_CHECKING:
    from .app import App

log = logging.getLogger("rich")


@rich.repr.auto
class View(Widget):
    def __init__(self, layout: Layout = None, name: str | None = None) -> None:
        self.layout: Layout = layout or DockLayout()
        self.mouse_over: Widget | None = None
        self.focused: Widget | None = None
        self.size = Dimensions(0, 0)
        self.widgets: set[Widget] = set()
        self.named_widgets: dict[str, Widget] = {}
        super().__init__(name)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        return
        yield

    def __rich_repr__(self) -> rich.repr.RichReprResult:
        yield "name", self.name

    @property
    def is_root_view(self) -> bool:
        return self.parent is self.app

    def is_mounted(self, widget: Widget) -> bool:
        return widget in self.widgets

    def render(self) -> RenderableType:
        return self.layout

    async def message_update(self, message: UpdateMessage) -> None:
        widget = message.widget
        assert isinstance(widget, Widget)
        display_update = self.root_view.layout.update_widget(self.console, widget)
        if display_update is not None:
            self.app.display(display_update)

    async def message_layout(self, message: LayoutMessage) -> None:
        log.debug("MESSAGE_LAYOUT %r", self.root_view)

        await self.root_view.refresh_layout()

    # async def on_create(self, event: events.Created) -> None:
    #     await self.mount(Header(self.title))

    async def mount(self, *anon_widgets: Widget, **widgets: Widget) -> None:

        name_widgets: Iterable[tuple[str | None, Widget]]
        name_widgets = chain(
            ((None, widget) for widget in anon_widgets), widgets.items()
        )
        for name, widget in name_widgets:
            name = name or widget.name
            if name:
                self.named_widgets[name] = widget
            await self.app.register(widget)
            widget.set_parent(self)
            await widget.post_message(events.Mount(sender=self))
            self.widgets.add(widget)

        self.require_repaint()

    async def refresh_layout(self) -> None:

        if not self.size:
            return

        width, height = self.console.size
        self.layout.reflow(width, height)
        self.app.refresh()

        for widget, region in self.layout:
            if isinstance(widget, Widget):
                await widget.post_message(
                    events.Resize(self, region.width, region.height)
                )

    async def on_resize(self, event: events.Resize) -> None:
        log.debug("view.on_resize")
        self.size = Dimensions(event.width, event.height)
        await self.refresh_layout()

    async def _on_mouse_move(self, event: events.MouseMove) -> None:
        try:
            widget, region = self.layout.get_widget_at(event.x, event.y)
        except NoWidget:
            await self.app.set_mouse_over(None)
        else:
            await self.app.set_mouse_over(widget)

            await widget.forward_event(
                events.MouseMove(
                    self,
                    event.x - region.x,
                    event.y - region.y,
                    event.delta_x,
                    event.delta_y,
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
            pass
            # try:
            #     widget, region = self.get_widget_at(event.x, event.y, deep=True)
            # except NoWidget:
            #     if isinstance(event, events.MouseDown):
            #         await self.app.set_focus(None)
            # else:
            #     if isinstance(event, events.MouseDown):
            #         await self.app.set_focus(widget)
            #     await widget.forward_event(event.offset(-region.x, -region.y))

        elif isinstance(event, (events.MouseScrollDown, events.MouseScrollUp)):
            pass
            # try:
            #     widget, _region = self.get_widget_at(event.x, event.y, deep=True)
            # except NoWidget:
            #     return
            # scroll_widget = widget or self.focused
            # if scroll_widget is not None:
            #     await scroll_widget.forward_event(event)
        else:
            if self.focused is not None:
                await self.focused.forward_event(event)

    async def action_toggle(self, name: str) -> None:
        log.debug("%r", self.named_widgets)
        widget = self.named_widgets[name]
        widget.visible = not widget.visible
        await self.refresh_layout()


class DoNotSet:
    pass


do_not_set = DoNotSet()


class DockView(View):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(layout=DockLayout(), name=name)

    async def dock(
        self,
        *widgets: Widget,
        edge: DockEdge = "top",
        z: int = 0,
        size: int | None | DoNotSet = do_not_set,
    ) -> Widget | tuple[Widget, ...]:

        dock = Dock(edge, widgets, z)
        assert isinstance(self.layout, DockLayout)
        self.layout.docks.append(dock)
        for widget in widgets:
            if size is not do_not_set:
                widget.layout_size = cast(Optional[int], size)
            if not self.is_mounted(widget):
                await self.mount(widget)
        await self.refresh_layout()

        widget, *rest = widgets
        if rest:
            return widgets
        else:
            return widget
