from rich.align import Align
from rich.text import Text

from textual.app import App
from textual import events
from textual.view import View
from textual.widgets import Button, Static
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

        layout = GridLayout(gap=(2, 1), gutter=1, align=("center", "center"))
        await self.push_view(View(layout=layout))

        layout.add_column("col", max_size=20, repeat=4)
        layout.add_row("numbers", min_size=3, max_size=6)
        layout.add_row("row", max_size=10, repeat=5)

        layout.add_areas(
            numbers="col1-start|col4-end,numbers",
            zero="col1-start|col2-end,row5",
            dot="col3,row4",
            equals="col4,row4",
        )

        def make_text(text: str) -> Text:
            return Text(font.renderText(text).rstrip("\n"), style="bold")

        def make_button(text: str) -> Button:
            label = make_text(text)
            return Button(label, style="white on rgb(51,51,51)")

        buttons = {
            name: make_button(name)
            for name in "AC,+/-,%,/,7,8,9,X,4,5,6,-,1,2,3,+,.,=".split(",")
        }

        for name in ("AC", "+/-", "%"):
            buttons[name].style = "#000000 on rgb(165,165,165)"
        for name in "/X-+=":
            buttons[name].style = "#ffffff on rgb(255,159,7)"

        zero_text = make_text("0")
        layout.place(
            *buttons.values(),
            numbers=Static(Align.right(zero_text)),
            zero=make_button("0"),
        )


GridTest.run(title="Calculator Test")
