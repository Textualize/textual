from rich.panel import Panel

from textual.app import App, ComposeResult
from textual import events
from textual.containers import Horizontal
from textual.widgets import Button, Header, TextLog


INSTRUCTIONS = """\
Press some keys!    

Because we want to display all the keys, ctrl+C won't quit this example. Use the Quit button below to exit the app.\
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

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            Button("Clear", id="clear", variant="warning"),
            Button("Quit", id="quit", variant="error"),
            id="buttons",
        )
        yield KeyLog()

    def on_ready(self) -> None:
        self.query_one(KeyLog).write(Panel(INSTRUCTIONS), expand=True)

    def on_key(self, event: events.Key) -> None:
        self.query_one(KeyLog).write(event)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.exit()
        elif event.button.id == "clear":
            self.query_one(KeyLog).clear()


app = KeysApp()

if __name__ == "__main__":
    app.run()
