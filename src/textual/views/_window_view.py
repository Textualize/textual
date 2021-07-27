from __future__ import annotations

from ..layouts.vertical import VerticalLayout
from ..view import View
from ..widget import Widget


class WindowView(View, layout=VerticalLayout):
    def __init__(
        self, *, gutter: tuple[int, int] = (1, 1), name: str | None = None
    ) -> None:
        self.gutter = gutter
        super().__init__(name=name)

    async def update(self, widget: Widget) -> None:
        self.layout = VerticalLayout(gutter=self.gutter)
        self.layout.add(widget)
