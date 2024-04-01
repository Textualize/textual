"""
An implementation of a classic calculator, with a layout inspired by macOS calculator.

Works like a real calculator. Click the buttons or press the equivalent keys.
"""

from decimal import Decimal

from textual import events, on
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.css.query import NoMatches
from textual.reactive import var
from textual.widgets import Button, Digits


class CalculatorApp(App):
    """A working 'desktop' calculator."""

    CSS_PATH = "calculator.tcss"

    numbers = var("0")
    show_ac = var(True)
    left = var(Decimal("0"))
    right = var(Decimal("0"))
    value = var("")
    operator = var("plus")

    # Maps button IDs on to the corresponding key name
    NAME_MAP = {
        "asterisk": "multiply",
        "slash": "divide",
        "underscore": "plus-minus",
        "full_stop": "point",
        "plus_minus_sign": "plus-minus",
        "percent_sign": "percent",
        "equals_sign": "equals",
        "minus": "minus",
        "plus": "plus",
    }

    def watch_numbers(self, value: str) -> None:
        """Called when numbers is updated."""
        self.query_one("#numbers", Digits).update(value)

    def compute_show_ac(self) -> bool:
        """Compute switch to show AC or C button"""
        return self.value in ("", "0") and self.numbers == "0"

    def watch_show_ac(self, show_ac: bool) -> None:
        """Called when show_ac changes."""
        self.query_one("#c").display = not show_ac
        self.query_one("#ac").display = show_ac

    def compose(self) -> ComposeResult:
        """Add our buttons."""
        with Container(id="calculator"):
            yield Digits(id="numbers")
            yield Button("AC", id="ac", variant="primary")
            yield Button("C", id="c", variant="primary")
            yield Button("+/-", id="plus-minus", variant="primary")
            yield Button("%", id="percent", variant="primary")
            yield Button("÷", id="divide", variant="warning")
            yield Button("7", id="number-7", classes="number")
            yield Button("8", id="number-8", classes="number")
            yield Button("9", id="number-9", classes="number")
            yield Button("×", id="multiply", variant="warning")
            yield Button("4", id="number-4", classes="number")
            yield Button("5", id="number-5", classes="number")
            yield Button("6", id="number-6", classes="number")
            yield Button("-", id="minus", variant="warning")
            yield Button("1", id="number-1", classes="number")
            yield Button("2", id="number-2", classes="number")
            yield Button("3", id="number-3", classes="number")
            yield Button("+", id="plus", variant="warning")
            yield Button("0", id="number-0", classes="number")
            yield Button(".", id="point")
            yield Button("=", id="equals", variant="warning")

    def on_key(self, event: events.Key) -> None:
        """Called when the user presses a key."""

        def press(button_id: str) -> None:
            """Press a button, should it exist."""
            try:
                self.query_one(f"#{button_id}", Button).press()
            except NoMatches:
                pass

        key = event.key
        if key.isdecimal():
            press(f"number-{key}")
        elif key == "c":
            press("c")
            press("ac")
        else:
            button_id = self.NAME_MAP.get(key)
            if button_id is not None:
                press(self.NAME_MAP.get(key, key))

    @on(Button.Pressed, ".number")
    def number_pressed(self, event: Button.Pressed) -> None:
        """Pressed a number."""
        assert event.button.id is not None
        number = event.button.id.partition("-")[-1]
        self.numbers = self.value = self.value.lstrip("0") + number

    @on(Button.Pressed, "#plus-minus")
    def plus_minus_pressed(self) -> None:
        """Pressed + / -"""
        self.numbers = self.value = str(Decimal(self.value or "0") * -1)

    @on(Button.Pressed, "#percent")
    def percent_pressed(self) -> None:
        """Pressed %"""
        self.numbers = self.value = str(Decimal(self.value or "0") / Decimal(100))

    @on(Button.Pressed, "#point")
    def pressed_point(self) -> None:
        """Pressed ."""
        if "." not in self.value:
            self.numbers = self.value = (self.value or "0") + "."

    @on(Button.Pressed, "#ac")
    def pressed_ac(self) -> None:
        """Pressed AC"""
        self.value = ""
        self.left = self.right = Decimal(0)
        self.operator = "plus"
        self.numbers = "0"

    @on(Button.Pressed, "#c")
    def pressed_c(self) -> None:
        """Pressed C"""
        self.value = ""
        self.numbers = "0"

    def _do_math(self) -> None:
        """Does the math: LEFT OPERATOR RIGHT"""
        try:
            if self.operator == "plus":
                self.left += self.right
            elif self.operator == "minus":
                self.left -= self.right
            elif self.operator == "divide":
                self.left /= self.right
            elif self.operator == "multiply":
                self.left *= self.right
            self.numbers = str(self.left)
            self.value = ""
        except Exception:
            self.numbers = "Error"

    @on(Button.Pressed, "#plus,#minus,#divide,#multiply")
    def pressed_op(self, event: Button.Pressed) -> None:
        """Pressed one of the arithmetic operations."""
        self.right = Decimal(self.value or "0")
        self._do_math()
        assert event.button.id is not None
        self.operator = event.button.id

    @on(Button.Pressed, "#equals")
    def pressed_equals(self) -> None:
        """Pressed ="""
        if self.value:
            self.right = Decimal(self.value)
        self._do_math()


if __name__ == "__main__":
    CalculatorApp().run(inline=True)
