from rich.panel import Panel

from textual.app import App, ComposeResult
from textual import events
from textual.widgets import Header, Footer, TextLog


class KeyLog(TextLog, inherit_bindings=False):
    """We don't want to handle scroll keys."""


class KeysApp(App):
    """Show key events in a text log."""

    TITLE = "Textual Keys"

    BINDINGS = [("c", "clear", "Clear")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield KeyLog()

    def on_ready(self) -> None:
        self.query_one(KeyLog).write(Panel("Press some keys!"))

    def on_key(self, event: events.Key) -> None:
        self.query_one(KeyLog).write(event)

    def action_clear(self) -> None:
        self.query_one(KeyLog).clear()


app = KeysApp()

if __name__ == "__main__":
    app.run()
