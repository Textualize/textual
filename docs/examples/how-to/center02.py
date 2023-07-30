from textual.app import App, ComposeResult
from textual.widgets import Static


class CenterApp(App):
    """How to center things."""

    CSS = """
    Screen {
        align: center middle;
    }

    #hello {
        background: blue 50%;
        border: wide white;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("Hello, World!", id="hello")


if __name__ == "__main__":
    app = CenterApp()
    app.run()
