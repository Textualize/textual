from textual.app import App
from textual import events
from textual.view import View
from textual.widgets import Placeholder
from textual.layouts.grid import GridLayout


class GridTest(App):
    async def on_load(self, event: events.Load) -> None:
        await self.bind("q,ctrl+c", "quit", "Quit")

    async def on_startup(self, event: events.Startup) -> None:

        layout = GridLayout()
        await self.push_view(View(layout=layout))

        layout.add_column(fraction=1, name="left", min_size=20)
        layout.add_column(size=30, name="center")
        layout.add_column(fraction=1, name="right")

        layout.add_row(fraction=1, name="top", min_size=2)
        layout.add_row(fraction=2, name="middle")
        layout.add_row(fraction=1, name="bottom")

        layout.add_areas(
            area1="left,top",
            area2="center,middle",
            area3="left-start|right-end,bottom",
            area4="right,top-start|middle-end",
        )

        layout.place(
            area1=Placeholder(name="area1"),
            area2=Placeholder(name="area2"),
            area3=Placeholder(name="area3"),
            area4=Placeholder(name="area4"),
        )


GridTest.run(title="Grid Test")
