from rich.text import Text

from textual.app import App
from textual import events
from textual.view import View
from textual.widgets import Button, Placeholder
from textual.layouts.grid import GridLayout

try:
    from pyfiglet import Figlet
except ImportError:
    print("Please install pyfiglet to run this example")

font = Figlet(font="small")


class GridTest(App):
    async def on_load(self, event: events.Load) -> None:
        await self.bind("q,ctrl+c", "quit", "Quit")

    async def on_startup(self, event: events.Startup) -> None:

        layout = GridLayout(gap=1, gutter=1, align=("center", "center"))
        await self.push_view(View(layout=layout))

        layout.add_column("col", max_size=20, repeat=4)
        layout.add_row("numbers", min_size=3, max_size=10)
        layout.add_row("row", max_size=10, repeat=4)

        layout.add_areas(
            numbers="col1-start|col4-end,numbers",
            zero="col1-start|col2-end,row4",
            dot="col3,row4",
            equals="col4,row4",
        )

        def make_button(text: str) -> Button:
            label = Text(font.renderText(text).rstrip("\n"), style="bold")
            return Button(label)

        buttons = {
            name: make_button(name)
            for name in "AC,+/-,%,/,7,8,9,X,4,5,6,-,1,2,3,+,.,=".split(",")
        }

        layout.place(
            *buttons.values(),
            numbers=Placeholder(name="numbers"),
            zero=make_button("0"),
        )


GridTest.run(title="Calculator Test")
