from __future__ import annotations

from rich.console import RenderableType

from .. import events
from ..geometry import Offset, Size
from ..layouts.vertical import VerticalLayout
from ..view import View
from ..message import Message
from ..widget import Widget
from ..widgets import Static


class VirtualSizeChange(Message):
    pass


class WindowView(View, layout=VerticalLayout):
    def __init__(
        self,
        widget: RenderableType | Widget,
        *,
        gutter: tuple[int, int] = (0, 1),
        name: str | None = None
    ) -> None:
        self.gutter = gutter
        layout = VerticalLayout(gutter=gutter)
        self.widget = widget if isinstance(widget, Widget) else Static(widget)
        layout.add(self.widget)
        super().__init__(name=name, layout=layout)

    async def update(self, widget: Widget | RenderableType) -> None:
        layout = self.layout
        assert isinstance(layout, VerticalLayout)
        layout.clear()
        self.widget = widget if isinstance(widget, Widget) else Static(widget)
        layout.add(self.widget)
        await self.refresh_layout()
        self.require_layout()
        await self.emit(VirtualSizeChange(self))

    async def watch_virtual_size(self, size: Size) -> None:
        await self.emit(VirtualSizeChange(self))

    async def on_resize(self, event: events.Resize) -> None:
        # self.layout.renders.pop(self.widget)
        self.require_repaint()
