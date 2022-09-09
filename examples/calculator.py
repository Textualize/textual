from decimal import Decimal

from textual.app import App, ComposeResult
from textual import events
from textual.layout import Container
from textual.reactive import var
from textual.widgets import Button, Static


class CalculatorApp(App):
    """A working 'desktop' calculator."""

    numbers = var("0")
    show_ac = var(True)
    left = var(Decimal("0"))
    right = var(Decimal("0"))
    value = var("")
    operator = var("plus")

    KEY_MAP = {
        "+": "plus",
        "-": "minus",
        ".": "point",
        "*": "multiply",
        "/": "divide",
        "_": "plus-minus",
        "%": "percent",
        "=": "equals",
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
        yield Container(
            Static(id="numbers"),
            Button("AC", id="ac", variant="primary"),
            Button("C", id="c", variant="primary"),
            Button("+/-", id="plus-minus", variant="primary"),
            Button("%", id="percent", variant="primary"),
            Button("÷", id="divide", variant="warning"),
            Button("7", id="number-7"),
            Button("8", id="number-8"),
            Button("9", id="number-9"),
            Button("×", id="multiply", variant="warning"),
            Button("4", id="number-4"),
            Button("5", id="number-5"),
            Button("6", id="number-6"),
            Button("-", id="minus", variant="warning"),
            Button("1", id="number-1"),
            Button("2", id="number-2"),
            Button("3", id="number-3"),
            Button("+", id="plus", variant="warning"),
            Button("0", id="number-0"),
            Button(".", id="point"),
            Button("=", id="equals", variant="warning"),
            id="calculator",
        )

    def on_key(self, event: events.Key) -> None:
        """Called when the user presses a key."""

        def press(button_id: str) -> None:
            self.query_one(f"#{button_id}", Button).press()
            self.set_focus(None)

        key = event.key
        if key.isdecimal():
            press(f"number-{key}")
        elif key == "c":
            press("c")
            press("ac")
        elif key in self.KEY_MAP:
            press(self.KEY_MAP[key])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Called when a button is pressed."""

        button_id = event.button.id
        assert button_id is not None

        self.bell()  # Terminal bell

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


app = CalculatorApp(css_path="calculator.css")
if __name__ == "__main__":
    app.run()
