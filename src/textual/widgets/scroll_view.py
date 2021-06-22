from __future__ import annotations

from rich.layout import Layout
from rich.text import Text

from .. import events
from ..scrollbar import ScrollBar

from ..page import Page
from ..view import LayoutView
from ..widget import StaticWidget


class ScrollView(LayoutView):
    def __init__(self, name: str | None = None) -> None:
        layout = Layout()
        layout.split_row(
            Layout(name="main", ratio=1), Layout(name="vertical_scrollbar", size=1)
        )
        layout["main"].split_column(
            Layout(name="content", ratio=1), Layout(name="horizontal_scrollbar", size=1)
        )
        self._vertical_scrollbar = ScrollBar(vertical=True)
        self._horizontal_Scrollbar = ScrollBar(vertical=False)
        super().__init__(layout=layout, name=name)

    async def on_mount(self, event: events.Mount) -> None:
        text = Text.from_markup("Hello, [@click='bell']World[/]!")
        await self.mount_all(
            content=StaticWidget(text),
            vertical_scrollbar=StaticWidget(self._vertical_scrollbar),
            horizontal_scrollbar=StaticWidget(self._horizontal_Scrollbar),
        )