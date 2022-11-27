from textual.app import App, ComposeResult
from textual.widgets import TextLog
from textual import events


class InputApp(App):
    """App to display key events."""

    def compose(self) -> ComposeResult:
        yield TextLog()

    def on_key(self, event: events.Key) -> None:
        self.query_one(TextLog).write(event)

    def key_space(self) -> None:
        self.bell()


if __name__ == "__main__":
    app = InputApp()
    app.run()
