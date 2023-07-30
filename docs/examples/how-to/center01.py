from textual.app import App, ComposeResult
from textual.widgets import Static


class CenterApp(App):
    """How to center things."""

    CSS = """
    Screen {
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("Hello, World!")


if __name__ == "__main__":
    app = CenterApp()
    app.run()
