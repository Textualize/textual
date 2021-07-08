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
        view = await self.push_view(View(layout=layout))

        layout.add_column(fraction=1, name="left", minimum_size=20)
        layout.add_column(size=30, name="center")
        layout.add_column(fraction=1, name="right")

        layout.add_row(fraction=1, name="top")
        layout.add_row(fraction=2, name="middle")
        layout.add_row(fraction=1, name="bottom")

        layout.add_area("area1", "left", "top")
        layout.add_area("area2", "center", "middle")
        layout.add_area("area3", ("left-start", "right-end"), "bottom")
        layout.add_area("area4", "right", ("top-start", "middle-end"))

        await view.mount(layout.add_widget(Placeholder(name="area1"), "area1"))
        await view.mount(layout.add_widget(Placeholder(name="area2"), "area2"))
        await view.mount(layout.add_widget(Placeholder(name="area3"), "area3"))
        await view.mount(layout.add_widget(Placeholder(name="area4"), "area4"))


GridTest.run(title="Grid Test")