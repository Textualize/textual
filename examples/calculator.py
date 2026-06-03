"""
A high-speed, zero-lag scientific calculator.
Features a static layout, dual-language support, and dynamic themes.
"""

from decimal import Decimal
import math

from textual import events, on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.css.query import NoMatches
from textual.reactive import var
from textual.widgets import Button, Label, Header

class CalculatorApp(App):
    CSS_PATH = "calculator.tcss"
    PREVENT_DOM_EVENTS = {events.MouseMove, events.MouseScrollUp, events.MouseScrollDown, events.Enter, events.Leave}

    dark_mode = var(True)
    lang = var("tr")

    numbers = var("0")
    left = var(Decimal("0"))
    right = var(Decimal("0"))
    value = var("")
    operator = var("plus")

    NAME_MAP = {
        "asterisk": "multiply", "slash": "divide", "underscore": "plus-minus",
        "full_stop": "point", "plus_minus_sign": "plus-minus",
        "percent_sign": "percent", "equals_sign": "equals",
        "minus": "minus", "plus": "plus",
    }

    DICTIONARY = {
        "tr": {"title": "Bilimsel Hesap Makinesi", "subtitle": "Tema: [T] | Dil: [L]", "error": "Hata"},
        "en": {"title": "Scientific Calculator", "subtitle": "Theme: [T] | Lang: [L]", "error": "Error"},
    }

    def on_mount(self) -> None:
        self.add_class("dark-theme")
        self.update_ui_text()

    def update_ui_text(self) -> None:
        tr = self.DICTIONARY[self.lang]
        self.title = tr["title"]
        self.sub_title = tr["subtitle"]
        try:
            self.query_one("#toggle-lang", Button).label = "TR/EN"
            self.query_one("#toggle-theme", Button).label = "Tema 🌓" if self.lang == "tr" else "Theme 🌓"
        except NoMatches:
            pass

    def render_display(self, value: str) -> str:
        # Ekran taşmasını engellemek için 14 karakter sınırı
        max_chars = 14
        value = value or "0"
        if len(value) > max_chars:
            value = value[:max_chars]
        return value

    def watch_numbers(self, value: str) -> None:
        try:
            self.query_one("#dev-ekran", Label).update(self.render_display(value))
        except NoMatches:
            pass

    def watch_dark_mode(self, dark_mode: bool) -> None:
        if dark_mode:
            self.remove_class("light-theme")
            self.add_class("dark-theme")
        else:
            self.remove_class("dark-theme")
            self.add_class("light-theme")

    def watch_lang(self, lang: str) -> None:
        self.update_ui_text()

    def on_key(self, event: events.Key) -> None:
        key = event.key.lower()
        if key == "t":
            self.dark_mode = not self.dark_mode
            return
        if key == "l":
            self.lang = "en" if self.lang == "tr" else "tr"
            return

        def press(btn: str):
            try: self.query_one(f"#{btn}", Button).press()
            except NoMatches: pass

        if key.isdecimal(): press(f"number-{key}")
        elif key == "c": press("c"); press("ac")
        else: press(self.NAME_MAP.get(key, ""))

    @on(Button.Pressed, "#toggle-theme")
    def toggle_theme_btn(self) -> None: self.dark_mode = not self.dark_mode

    @on(Button.Pressed, "#toggle-lang")
    def toggle_lang_btn(self) -> None: self.lang = "en" if self.lang == "tr" else "tr"

    @on(Button.Pressed, ".number")
    def number_pressed(self, event: Button.Pressed) -> None:
        number = event.button.id.split("-")[-1]
        if self.value in ("", "0"): self.value = number
        else: self.value += number
        self.numbers = self.value

    @on(Button.Pressed, "#plus-minus")
    def plus_minus_pressed(self) -> None:
        self.numbers = self.value = str(Decimal(self.value or "0") * -1)

    @on(Button.Pressed, "#percent")
    def percent_pressed(self) -> None:
        self.numbers = self.value = str(Decimal(self.value or "0") / Decimal(100))

    @on(Button.Pressed, "#point")
    def pressed_point(self) -> None:
        if "." not in self.value:
            self.value = (self.value or "0") + "."
            self.numbers = self.value

    @on(Button.Pressed, "#sqrt,#square,#cube,#sin,#cos,#tan,#log,#pi")
    def sci(self, event: Button.Pressed) -> None:
        try:
            x = float(self.value or self.numbers)
            op = event.button.id
            if op == "pi": r = math.pi
            elif op == "sqrt": r = math.sqrt(x)
            elif op == "square": r = x**2
            elif op == "cube": r = x**3
            elif op == "sin": r = math.sin(math.radians(x))
            elif op == "cos": r = math.cos(math.radians(x))
            elif op == "tan": r = math.tan(math.radians(x))
            elif op == "log": r = math.log10(x)
            self.value = self.numbers = str(round(r, 6))
        except Exception:
            self.value = ""
            self.numbers = self.DICTIONARY[self.lang]["error"]

    def _do_math(self) -> None:
        try:
            if self.operator == "plus": self.left += self.right
            elif self.operator == "minus": self.left -= self.right
            elif self.operator == "divide": self.left /= self.right
            elif self.operator == "multiply": self.left *= self.right
            self.value = ""
            self.numbers = str(self.left)
        except Exception:
            self.numbers = self.DICTIONARY[self.lang]["error"]

    @on(Button.Pressed, "#plus,#minus,#divide,#multiply")
    def op(self, event: Button.Pressed) -> None:
        self.right = Decimal(self.value or "0")
        self._do_math()
        self.operator = event.button.id

    @on(Button.Pressed, "#equals")
    def eq(self) -> None:
        if self.value: self.right = Decimal(self.value)
        self._do_math()

    @on(Button.Pressed, "#ac")
    def ac(self) -> None:
        self.value = ""
        self.left = self.right = Decimal(0)
        self.operator = "plus"
        self.numbers = "0"

    @on(Button.Pressed, "#c")
    def c(self) -> None:
        self.value = ""
        self.numbers = "0"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Horizontal(id="top-bar"):
            yield Button("TR/EN", id="toggle-lang", variant="default")
            yield Button("Tema", id="toggle-theme", variant="primary")
        with Container(id="calculator"):
            yield Label("0", id="dev-ekran")

            yield Button("sin", id="sin", variant="success")
            yield Button("cos", id="cos", variant="success")
            yield Button("tan", id="tan", variant="success")
            yield Button("log", id="log", variant="success")

            yield Button("√", id="sqrt", variant="success")
            yield Button("x²", id="square", variant="success")
            yield Button("x³", id="cube", variant="success")
            yield Button("π", id="pi", variant="success")

            yield Button("AC", id="ac", variant="primary")
            yield Button("C", id="c", variant="primary")
            yield Button("+/-", id="plus-minus", variant="primary")
            yield Button("%", id="percent", variant="primary")

            yield Button("7", id="number-7", classes="number")
            yield Button("8", id="number-8", classes="number")
            yield Button("9", id="number-9", classes="number")
            yield Button("÷", id="divide", variant="warning")

            yield Button("4", id="number-4", classes="number")
            yield Button("5", id="number-5", classes="number")
            yield Button("6", id="number-6", classes="number")
            yield Button("×", id="multiply", variant="warning")

            yield Button("1", id="number-1", classes="number")
            yield Button("2", id="number-2", classes="number")
            yield Button("3", id="number-3", classes="number")
            yield Button("-", id="minus", variant="warning")

            yield Button("0", id="number-0", classes="number")
            yield Button(".", id="point")
            yield Button("=", id="equals", variant="warning")
            yield Button("+", id="plus", variant="warning")

if __name__ == "__main__":
    CalculatorApp().run()