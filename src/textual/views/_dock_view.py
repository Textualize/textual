from __future__ import annotations
from typing import cast, Optional

from ..layouts.dock import DockLayout, Dock, DockEdge
from ..layouts.grid import GridLayout, GridAlign
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
        name: str | None = None,
        id: str | None = None,
        edge: DockEdge = "top",
        z: int = 0,
        size: int | None | DoNotSet = do_not_set,
    ) -> None:

        dock = Dock(edge, widgets, z)
        assert isinstance(self.layout, DockLayout)
        self.layout.docks.append(dock)
        for widget in widgets:
            if id is not None:
                widget._id = id
            if name is not None:
                widget.name = name
            if size is not do_not_set:
                widget.layout_size = cast(Optional[int], size)
            if name is None:
                await self.mount(widget)
            else:
                await self.mount(**{name: widget})
        await self.refresh_layout()

    async def dock_grid(
        self,
        *,
        name: str | None = None,
        id: str | None = None,
        edge: DockEdge = "top",
        z: int = 0,
        size: int | None | DoNotSet = do_not_set,
        gap: tuple[int, int] | int | None = None,
        gutter: tuple[int, int] | int | None = None,
        align: tuple[GridAlign, GridAlign] | None = None,
    ) -> GridLayout:

        grid = GridLayout(gap=gap, gutter=gutter, align=align)
        view = View(layout=grid, id=id, name=name)
        dock = Dock(edge, (view,), z)
        assert isinstance(self.layout, DockLayout)
        self.layout.docks.append(dock)
        if size is not do_not_set:
            view.layout_size = cast(Optional[int], size)
        if name is None:
            await self.mount(view)
        else:
            await self.mount(**{name: view})
        await self.refresh_layout()
        return grid
