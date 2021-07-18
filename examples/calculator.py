from decimal import Decimal

from rich.align import Align
from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.padding import Padding
from rich.text import Text


from textual.app import App
from textual import events
from textual.message import Message
from textual.reactive import Reactive
from textual.view import View
from textual.widget import Widget
from textual.widgets import Button
from textual.layouts.grid import GridLayout

try:
    from pyfiglet import Figlet
except ImportError:
    print("Please install pyfiglet to run this example")
    import sys

    sys.exit()


class FigletText:
    """A renderable to generate figlet text that adapts to fit the container."""

    def __init__(self, text: str) -> None:
        self.text = text

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        size = min(options.max_width / 2, options.max_height)
        if size < 4:
            yield Text(self.text, style="bold")
        else:
            if size < 7:
                font_name = "mini"
            elif size < 8:
                font_name = "small"
            elif size < 10:
                font_name = "standard"
            else:
                font_name = "big"
            font = Figlet(font=font_name, width=options.max_width)
            yield Text(font.renderText(self.text).rstrip("\n"), style="bold")


class Numbers(Widget):
    """The digital display of the calculator."""

    value: Reactive[str] = Reactive("0")

    def render(self) -> RenderableType:
        return Padding(
            Align.right(FigletText(self.value), vertical="middle"),
            (0, 1),
            style="white on rgb(51,51,51)",
        )


class CalculatorApp(App):
    """A working calculator app."""

    async def on_load(self, event: events.Load) -> None:
        """Sent when the app starts, but before displaying anything."""

        self.left = Decimal("0")
        self.right = Decimal("0")
        self.value = ""
        self.operator = "+"
        self.numbers = Numbers()

        def make_button(text: str, style: str) -> Button:
            """Create a button with the given Figlet label."""
            return Button(FigletText(text), style=style, name=text)

        dark = "white on rgb(51,51,51)"
        light = "black on rgb(165,165,165)"
        yellow = "white on rgb(255,159,7)"

        button_styles = {
            "AC": light,
            "C": light,
            "+/-": light,
            "%": light,
            "/": yellow,
            "X": yellow,
            "-": yellow,
            "+": yellow,
            "=": yellow,
        }

        # Make all the buttons
        self.buttons = {
            name: make_button(name, button_styles.get(name, dark))
            for name in "+/-,%,/,7,8,9,X,4,5,6,-,1,2,3,+,.,=".split(",")
        }

        self.zero = make_button("0", dark)
        self.ac = make_button("AC", light)
        self.c = make_button("C", light)
        self.c.visible = False

    async def on_startup(self, event: events.Startup) -> None:
        """Sent when the app has gone full screen."""

        # Create a grid layout
        grid = await self.view.dock_grid(
            gap=(2, 1), gutter=1, align=("center", "center")
        )

        # Create rows / columns / areas
        grid.add_column("col", max_size=30, repeat=4)
        grid.add_row("numbers", max_size=15)
        grid.add_row("row", max_size=15, repeat=5)
        grid.add_areas(
            clear="col1,row1",
            numbers="col1-start|col4-end,numbers",
            zero="col1-start|col2-end,row5",
        )
        # Place out widgets in to the layout
        grid.place(clear=self.c)
        grid.place(
            *self.buttons.values(), clear=self.ac, numbers=self.numbers, zero=self.zero
        )

    async def message_button_pressed(self, message: Message) -> None:
        """A message sent by the button widget"""

        assert isinstance(message.sender, Button)
        button_name = message.sender.name

        def do_math() -> bool:
            operator = self.operator
            right = self.right
            if operator == "+":
                self.left += right
            elif operator == "-":
                self.left -= right
            elif operator == "/":
                try:
                    self.left /= right
                except ZeroDivisionError:
                    self.numbers.value = "Error"
                    return False
            elif operator == "X":
                self.left *= right
            return True

        if button_name.isdigit():
            self.value = self.value.lstrip("0") + button_name
            self.numbers.value = self.value
        elif button_name == "+/-":
            self.value = str(Decimal(self.value or "0") * -1)
            self.numbers.value = self.value
        elif button_name == "%":
            self.value = str(Decimal(self.value or "0") / Decimal(100))
            self.numbers.value = self.value
        elif button_name == ".":
            if "." not in self.value:
                self.value += "."
                self.numbers.value = self.value
        elif button_name == "AC":
            self.value = ""
            self.left = self.right = Decimal(0)
            self.operator = "+"
            self.numbers.value = "0"
        elif button_name == "C":
            self.value = ""
            self.numbers.value = "0"
        elif button_name in ("+", "-", "/", "X"):
            self.right = Decimal(self.value or "0")
            if do_math():
                self.numbers.value = str(self.left)
            self.value = ""
            self.operator = button_name
        elif button_name == "=":
            if self.value:
                self.right = Decimal(self.value or "0")
            if do_math():
                self.numbers.value = str(self.left)
            self.value = ""

        show_ac = self.value in ("", "0") and self.numbers.value == "0"
        self.c.visible = not show_ac
        self.ac.visible = show_ac


CalculatorApp.run(title="Calculator Test")
