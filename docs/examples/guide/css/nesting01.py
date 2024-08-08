from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static


class NestingDemo(App):
    """App that doesn't have nested CSS."""

    CSS_PATH = "nesting01.tcss"

    def compose(self) -> ComposeResult:
        with Horizontal(id="status"):
            yield Static("Builder", classes="box done")
            yield Static("Test Runner", classes="box stopped")



if __name__ == "__main__":
    app = NestingDemo()
    app.run()
