from __future__ import annotations

from rich.panel import Panel
from rich.text import Text

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.reactive import Reactive, var
from textual.widgets import Button, Header, TextLog

INSTRUCTIONS = """\
[u]Press some keys![/]

To quit the app press [b]ctrl+c[/b] [i]twice[/i] or press the Quit button below.\
"""


class KeyLog(TextLog, inherit_bindings=False):
    """We don't want to handle scroll keys."""


class KeysApp(App, inherit_bindings=False):
    """Show key events in a text log."""

    TITLE = "Textual Keys"
    BINDINGS = [("c", "clear", "Clear")]
    CSS = """
    #buttons {
        dock: bottom;
        height: 3;
    }
    Button {
        width: 1fr;
    }
    """

    last_key: Reactive[str | None] = var(None)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            Button("Clear", id="clear", variant="warning"),
            Button("Quit", id="quit", variant="error"),
            id="buttons",
        )
        yield KeyLog()

    def on_ready(self) -> None:
        self.query_one(KeyLog).write(Panel(Text.from_markup(INSTRUCTIONS)), expand=True)

    def on_key(self, event: events.Key) -> None:
        self.query_one(KeyLog).write(event)
        if event.key == "ctrl+c":
            if self.last_key == "ctrl+c":
                self.exit()
            else:
                self.query_one(KeyLog).write("Press Ctrl+C again to quit")

        self.last_key = event.key

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.exit()
        elif event.button.id == "clear":
            self.query_one(KeyLog).clear()


app = KeysApp()

if __name__ == "__main__":
    app.run()
