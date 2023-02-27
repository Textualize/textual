from decimal import Decimal

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.css.query import NoMatches
from textual.reactive import var
from textual.widgets import Button, Static


class CalculatorApp(App):
    """A working 'desktop' calculator."""

    CSS_PATH = "calculator.css"

    numbers = var("0")
    show_ac = var(True)
    left = var(Decimal("0"))
    right = var(Decimal("0"))
    value = var("")
    operator = var("plus")

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
        # Update the Numbers widget
        self.query_one("#numbers", Static).update(value)

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
            yield Static(id="numbers")
            yield Button("AC", id="ac", variant="primary")
            yield Button("C", id="c", variant="primary")
            yield Button("+/-", id="plus-minus", variant="primary")
            yield Button("%", id="percent", variant="primary")
            yield Button("÷", id="divide", variant="warning")
            yield Button("7", id="number-7")
            yield Button("8", id="number-8")
            yield Button("9", id="number-9")
            yield Button("×", id="multiply", variant="warning")
            yield Button("4", id="number-4")
            yield Button("5", id="number-5")
            yield Button("6", id="number-6")
            yield Button("-", id="minus", variant="warning")
            yield Button("1", id="number-1")
            yield Button("2", id="number-2")
            yield Button("3", id="number-3")
            yield Button("+", id="plus", variant="warning")
            yield Button("0", id="number-0")
            yield Button(".", id="point")
            yield Button("=", id="equals", variant="warning")

    def on_key(self, event: events.Key) -> None:
        """Called when the user presses a key."""

        def press(button_id: str) -> None:
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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Called when a button is pressed."""

        button_id = event.button.id
        assert button_id is not None

        def do_math() -> None:
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

        if button_id.startswith("number-"):
            number = button_id.partition("-")[-1]
            self.numbers = self.value = self.value.lstrip("0") + number
        elif button_id == "plus-minus":
            self.numbers = self.value = str(Decimal(self.value or "0") * -1)
        elif button_id == "percent":
            self.numbers = self.value = str(Decimal(self.value or "0") / Decimal(100))
        elif button_id == "point":
            if "." not in self.value:
                self.numbers = self.value = (self.value or "0") + "."
        elif button_id == "ac":
            self.value = ""
            self.left = self.right = Decimal(0)
            self.operator = "plus"
            self.numbers = "0"
        elif button_id == "c":
            self.value = ""
            self.numbers = "0"
        elif button_id in ("plus", "minus", "divide", "multiply"):
            self.right = Decimal(self.value or "0")
            do_math()
            self.operator = button_id
        elif button_id == "equals":
            if self.value:
                self.right = Decimal(self.value)
            do_math()


if __name__ == "__main__":
    CalculatorApp().run()
