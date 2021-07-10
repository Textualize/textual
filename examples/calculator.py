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

        layout.add_column(name="col1", max_size=20)
        layout.add_column(name="col2", max_size=20)
        layout.add_column(name="col3", max_size=20)
        layout.add_column(name="col4", max_size=20)

        layout.add_row(name="numbers", max_size=10)
        layout.add_row(name="row1", max_size=10)
        layout.add_row(name="row2", max_size=10)
        layout.add_row(name="row3", max_size=10)
        layout.add_row(name="row4", max_size=10)

        layout.add_area("numbers", ("col1-start", "col4-end"), "numbers")
        layout.add_area("zero", ("col1-start", "col2-end"), "row4")
        layout.add_area("dot", "col3", "row4")
        layout.add_area("equals", "col4", "row4")

        layout.add_widget(Placeholder(name="numbers"), area="numbers")
        layout.add_widget(Placeholder(name="0"), area="zero")
        layout.add_widget(Placeholder(name="."), area="dot")
        layout.add_widget(Placeholder(name="="), area="equals")

        layout.set_gap(1)
        layout.set_align("center", "center")


GridTest.run(title="Calculator Test")