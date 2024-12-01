from textual.app import App, ComposeResult
from textual.widgets import Label


class PositionApp(App):
    CSS_PATH = "position.tcss"

    def compose(self) -> ComposeResult:
        yield Label("Absolute", id="label1")
        yield Label("Relative", id="label2")


if __name__ == "__main__":
    app = PositionApp()
    app.run()
