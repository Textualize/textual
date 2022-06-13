"""

A Textual app to create a fully working calculator, modelled after MacOS Calculator.

"""

from decimal import Decimal

from rich.align import Align
from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.padding import Padding
from rich.style import Style
from rich.text import Text

from textual.app import App
from textual.reactive import Reactive
from textual.views import GridView
from textual.widget import Widget
from textual.widgets import Button

try:
    from pyfiglet import Figlet
except ImportError:
    print("Please install pyfiglet to run this example")
    raise


class FigletText:
    """A renderable to generate figlet text that adapts to fit the container."""

    def __init__(self, text: str) -> None:
        self.text = text

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        """Build a Rich renderable to render the Figlet text."""
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

    value = Reactive("0")

    def render(self) -> RenderableType:
        """Build a Rich renderable to render the calculator display."""
        return Padding(
            Align.right(FigletText(self.value), vertical="middle"),
            (0, 1),
            style="white on rgb(51,51,51)",
        )


class Calculator(GridView):
    """A working calculator app."""

    DARK = "white on rgb(51,51,51)"
    LIGHT = "black on rgb(165,165,165)"
    YELLOW = "white on rgb(255,159,7)"

    BUTTON_STYLES = {
        "AC": LIGHT,
        "C": LIGHT,
        "+/-": LIGHT,
        "%": LIGHT,
        "/": YELLOW,
        "X": YELLOW,
        "-": YELLOW,
        "+": YELLOW,
        "=": YELLOW,
    }

    display = Reactive("0")
    show_ac = Reactive(True)

    def watch_display(self, value: str) -> None:
        """Called when self.display is modified."""
        # self.numbers is a widget that displays the calculator result
        # Setting the attribute value changes the display
        # This allows us to write self.display = "100" to update the display
        self.numbers.value = value

    def compute_show_ac(self) -> bool:
        """Compute show_ac reactive value."""
        # Condition to show AC button over C
        return self.value in ("", "0") and self.display == "0"

    def watch_show_ac(self, show_ac: bool) -> None:
        """When the show_ac attribute change we need to update the buttons."""
        # Show AC and hide C or vice versa
        self.c.display = not show_ac
        self.ac.display = show_ac

    def on_mount(self) -> None:
        """Event when widget is first mounted (added to a parent view)."""

        # Attributes to store the current calculation
        self.left = Decimal("0")
        self.right = Decimal("0")
        self.value = ""
        self.operator = "+"

        # The calculator display
        self.numbers = Numbers()
        self.numbers.style_border = "bold"

        def make_button(text: str, style: str) -> Button:
            """Create a button with the given Figlet label."""
            return Button(FigletText(text), style=style, name=text)

        # Make all the buttons
        self.buttons = {
            name: make_button(name, self.BUTTON_STYLES.get(name, self.DARK))
            for name in "+/-,%,/,7,8,9,X,4,5,6,-,1,2,3,+,.,=".split(",")
        }

        # Buttons that have to be treated specially
        self.zero = make_button("0", self.DARK)
        self.ac = make_button("AC", self.LIGHT)
        self.c = make_button("C", self.LIGHT)
        self.c.display = False

        # Set basic grid settings
        self.grid.set_gap(2, 1)
        self.grid.set_gutter(1)
        self.grid.set_align("center", "center")

        # Create rows / columns / areas
        self.grid.add_column("col", max_size=30, repeat=4)
        self.grid.add_row("numbers", max_size=15)
        self.grid.add_row("row", max_size=15, repeat=5)
        self.grid.add_areas(
            clear="col1,row1",
            numbers="col1-start|col4-end,numbers",
            zero="col1-start|col2-end,row5",
        )
        # Place out widgets in to the layout
        self.grid.place(clear=self.c)
        self.grid.place(
            *self.buttons.values(), clear=self.ac, numbers=self.numbers, zero=self.zero
        )

    def handle_button_pressed(self, message: ButtonPressed) -> None:
        """A message sent by the button widget"""

        assert isinstance(message.sender, Button)
        button_name = message.sender.name

        def do_math() -> None:
            """Does the math: LEFT OPERATOR RIGHT"""
            self.log(self.left, self.operator, self.right)
            try:
                if self.operator == "+":
                    self.left += self.right
                elif self.operator == "-":
                    self.left -= self.right
                elif self.operator == "/":
                    self.left /= self.right
                elif self.operator == "X":
                    self.left *= self.right
                self.display = str(self.left)
                self.value = ""
                self.log("=", self.left)
            except Exception:
                self.display = "Error"

        if button_name.isdigit():
            self.display = self.value = self.value.lstrip("0") + button_name
        elif button_name == "+/-":
            self.display = self.value = str(Decimal(self.value or "0") * -1)
        elif button_name == "%":
            self.display = self.value = str(Decimal(self.value or "0") / Decimal(100))
        elif button_name == ".":
            if "." not in self.value:
                self.display = self.value = (self.value or "0") + "."
        elif button_name == "AC":
            self.value = ""
            self.left = self.right = Decimal(0)
            self.operator = "+"
            self.display = "0"
        elif button_name == "C":
            self.value = ""
            self.display = "0"
        elif button_name in ("+", "-", "/", "X"):
            self.right = Decimal(self.value or "0")
            do_math()
            self.operator = button_name
        elif button_name == "=":
            if self.value:
                self.right = Decimal(self.value)
            do_math()


class CalculatorApp(App):
    """The Calculator Application"""

    async def on_mount(self) -> None:
        """Mount the calculator widget."""
        await self.screen.dock(Calculator())


CalculatorApp.run(title="Calculator Test", log_path="textual.log")
