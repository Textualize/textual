from textual.app import App, ComposeResult
from textual.widgets import Input
from textual.widgets import DigitDisplay


class MyApp(App):
    BINDINGS = []

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Type something:")
        yield DigitDisplay("")

    def on_input_changed(self, event: Input.Changed) -> None:
        display: DigitDisplay = self.query_one(DigitDisplay)
        display.digits = "".join(d for d in event.value if d in DigitDisplay.supported_digits)


if __name__ == "__main__":
    app = MyApp()
    app.run()
