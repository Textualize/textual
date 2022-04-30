from __future__ import annotations

from rich.console import RenderableType

from .. import events
from ..geometry import Size, SpacingDimensions
from ..layouts.vertical import VerticalLayout
from ..view import View
from ..message import Message
from .. import messages
from ..widget import Widget
from ..widgets import Static


class WindowChange(Message):
    def can_replace(self, message: Message) -> bool:
        return isinstance(message, WindowChange)


class WindowView(View, layout=VerticalLayout):
    def __init__(
        self,
        widget: RenderableType | Widget,
        *,
        auto_width: bool = False,
        gutter: SpacingDimensions = (0, 0),
        name: str | None = None,
    ) -> None:
        layout = VerticalLayout(gutter=gutter, auto_width=auto_width)
        self.widget = widget if isinstance(widget, Widget) else Static(widget)
        layout.add(self.widget)
        super().__init__(name=name, layout=layout)

    async def update(self, widget: Widget | RenderableType) -> None:
        layout = self.layout
        assert isinstance(layout, VerticalLayout)
        layout.clear()
        self.widget = widget if isinstance(widget, Widget) else Static(widget)
        layout.add(self.widget)
        self.layout.require_update()
        self.refresh(layout=True)
        await self.emit(WindowChange(self))

    async def handle_update(self, message: messages.Update) -> None:
        message.prevent_default()
        await self.emit(WindowChange(self))

    async def handle_layout(self, message: messages.Layout) -> None:
        self.log("TRANSLATING layout")
        self.layout.require_update()
        message.stop()
        self.refresh()

    async def watch_virtual_size(self, size: Size) -> None:
        await self.emit(WindowChange(self))

    async def watch_scroll_x(self, value: int) -> None:
        self.layout.require_update()
        self.refresh()

    async def watch_scroll_y(self, value: int) -> None:
        self.layout.require_update()
        self.refresh()

    async def on_resize(self, event: events.Resize) -> None:
        await self.emit(WindowChange(self))
