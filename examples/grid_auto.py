from textual.app import App
from textual import events
from textual.view import View
from textual.widgets import Placeholder
from textual.layouts.grid import GridLayout

import logging
from logging import FileHandler

logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[FileHandler("richtui.log")],
)

log = logging.getLogger("rich")


class GridTest(App):
    async def on_load(self, event: events.Load) -> None:
        await self.bind("q,ctrl+c", "quit", "Quit")

    async def on_startup(self, event: events.Startup) -> None:

        layout = GridLayout()
        await self.push_view(View(layout=layout))

        layout.add_column("col", fraction=1, max_size=20)
        layout.add_row("row", fraction=1, max_size=10)
        layout.set_repeat(True, True)
        layout.add_areas(center="col-2-start|col-4-end,row-2-start|row-3-end")
        layout.set_align("stretch", "center")

        # *(Placeholder() for _ in range(20)),
        layout.place(*(Placeholder() for _ in range(20)), center=Placeholder())

        # layout.add_column(fraction=1, name="left", min_size=20)
        # layout.add_column(size=30, name="center")
        # layout.add_column(fraction=1, name="right")

        # layout.add_row(fraction=1, name="top", min_size=2)
        # layout.add_row(fraction=2, name="middle")
        # layout.add_row(fraction=1, name="bottom")

        # layout.add_areas(
        #     area1="left,top",
        #     area2="center,middle",
        #     area3="left-start|right-end,bottom",
        #     area4="right,top-start|middle-end",
        # )

        # layout.place(
        #     area1=Placeholder(name="area1"),
        #     area2=Placeholder(name="area2"),
        #     area3=Placeholder(name="area3"),
        #     area4=Placeholder(name="area4"),
        # )


GridTest.run(title="Grid Test")
