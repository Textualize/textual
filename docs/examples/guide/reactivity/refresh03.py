from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Input, Label


class Name(Widget):
    """Generates a greeting."""

    who = reactive("name", recompose=True)  # (1)!

    def compose(self) -> ComposeResult:  # (2)!
        yield Label(f"Hello, {self.who}!")


class WatchApp(App):
    CSS_PATH = "refresh02.tcss"

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Enter your name")
        yield Name()

    def on_input_changed(self, event: Input.Changed) -> None:
        self.query_one(Name).who = event.value


if __name__ == "__main__":
    app = WatchApp()
    app.run()
