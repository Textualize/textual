from textual.app import App
from textual import events
from textual.view import View
from textual.widgets import Placeholder
from textual.layouts.grid import GridLayout


class GridTest(App):
    async def on_load(self, event: events.Load) -> None:
        await self.bind("q,ctrl+c", "quit", "Quit")

    async def on_startup(self, event: events.Startup) -> None:

        layout = GridLayout(gap=1, gutter=1, align=("center", "center"))
        await self.push_view(View(layout=layout))

        layout.add_column("col", max_size=20, repeat=4)
        layout.add_row("numbers", max_size=10)
        layout.add_row("row", max_size=10, repeat=4)

        layout.add_areas(
            numbers="col1-start|col4-end,numbers",
            zero="col1-start|col2-end,row4",
            dot="col3,row4",
            equals="col4,row4",
        )

        layout.place(
            numbers=Placeholder(name="numbers"),
            zero=Placeholder(name="0"),
            dot=Placeholder(name="."),
            equals=Placeholder(name="="),
        )


GridTest.run(title="Calculator Test")
