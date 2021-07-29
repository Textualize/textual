from __future__ import annotations

from rich.console import RenderableType

from ..geometry import Offset, Dimensions
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
        gutter: tuple[int, int] = (1, 1),
        name: str | None = None
    ) -> None:
        self.gutter = gutter
        layout = VerticalLayout()
        layout.add(widget if isinstance(widget, Widget) else Static(widget))
        super().__init__(name=name, layout=layout)

    async def update(self, widget: Widget | RenderableType) -> None:
        layout = self.layout
        assert isinstance(layout, VerticalLayout)
        layout.clear()
        layout.add(widget if isinstance(widget, Widget) else Static(widget))
        await self.refresh_layout()
        self.require_layout()

    async def watch_virtual_size(self, size: Dimensions) -> None:
        await self.emit(VirtualSizeChange(self))
