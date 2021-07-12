from rich.align import Align
from rich.console import Console, ConsoleOptions, RenderResult
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


class FigletText:
    """A renderable to generate figlet text that adapts to fit the container."""

    def __init__(self, text: str) -> None:
        self.text = text

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        size = min(options.max_width / 2, options.max_height)

        text = self.text
        if size < 4:
            yield Text(text, style="bold")
        else:
            if size < 7:
                font_name = "mini"
            elif size < 8:
                font_name = "small"
            elif size < 10:
                font_name = "standard"
            else:
                font_name = "big"
            font = Figlet(font=font_name)
            yield Text(font.renderText(text).rstrip("\n"), style="bold")


class CalculatorApp(App):
    async def on_startup(self, event: events.Startup) -> None:

        layout = GridLayout(gap=(2, 1), gutter=1, align=("center", "center"))
        await self.push_view(View(layout=layout))

        layout.add_column("col", max_size=30, repeat=4)
        layout.add_row("numbers")
        layout.add_row("row", max_size=15, repeat=5)
        layout.add_areas(
            numbers="col1-start|col4-end,numbers", zero="col1-start|col2-end,row5"
        )

        def make_button(text: str) -> Button:
            return Button(FigletText(text), style="white on rgb(51,51,51)")

        buttons = {
            name: make_button(name)
            for name in "AC,+/-,%,/,7,8,9,X,4,5,6,-,1,2,3,+,.,=".split(",")
        }
        for name in ("AC", "+/-", "%"):
            buttons[name].style = "black on rgb(165,165,165)"
        for name in "/X-+=":
            buttons[name].style = "white on rgb(255,159,7)"

        numbers = Align.right(FigletText("0"), vertical="middle")

        layout.place(
            *buttons.values(),
            numbers=Static(numbers, padding=(0, 1), style="white on rgb(51,51,51)"),
            zero=make_button("0"),
        )


CalculatorApp.run(title="Calculator Test")
