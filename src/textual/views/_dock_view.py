from __future__ import annotations
from typing import cast, Optional

from ..layouts.dock import DockLayout, Dock, DockEdge
from ..view import View
from ..widget import Widget


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
        name: str | None = None
    ) -> None:

        dock = Dock(edge, widgets, z)
        assert isinstance(self.layout, DockLayout)
        self.layout.docks.append(dock)
        for widget in widgets:
            if size is not do_not_set:
                widget.layout_size = cast(Optional[int], size)
            if not self.is_mounted(widget):
                if name is None:
                    await self.mount(widget)
                else:
                    await self.mount(**{name: widget})
        await self.refresh_layout()
