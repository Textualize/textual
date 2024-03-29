from textual.app import App, ComposeResult
from textual.widgets import Static


class VerticalLayoutExample(App):
    CSS_PATH = "vertical_layout.tcss"

    def compose(self) -> ComposeResult:
        yield Static("One", classes="box")
        yield Static("Two", classes="box")
        yield Static("Three", classes="box")


if __name__ == "__main__":
    app = VerticalLayoutExample()
    app.run()
