from textual.app import App, ComposeResult
from textual.widgets import Static


class CenterLayoutExample(App):
    CSS_PATH = "center_layout.css"

    def compose(self) -> ComposeResult:
        yield Static("One", id="bottom")
        yield Static("Two", id="middle")
        yield Static("Three", id="top")


if __name__ == "__main__":
    app = CenterLayoutExample()
    app.run()
