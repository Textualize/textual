from textual import events
from textual.app import App, ComposeResult
from textual.widgets import RichLog


class KeyLogger(RichLog):
    def on_key(self, event: events.Key) -> None:
        self.write(event)


class InputApp(App):
    """App to display key events."""

    CSS_PATH = "key03.tcss"

    def compose(self) -> ComposeResult:
        yield KeyLogger()
        yield KeyLogger()
        yield KeyLogger()
        yield KeyLogger()


if __name__ == "__main__":
    app = InputApp()
    app.run()
