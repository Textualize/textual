from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Input


class Name(Widget):
    """Generates a greeting."""

    who = reactive("name")

    def render(self) -> str:
        return f"Hello, {self.who}!"


class WatchApp(App):
    CSS_PATH = "refresh01.css"

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Enter your name")
        yield Name()

    def on_input_changed(self, event: Input.Changed) -> None:
        self.query_one(Name).who = event.value


if __name__ == "__main__":
    app = WatchApp()
    app.run()
