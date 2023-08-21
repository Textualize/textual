from textual.app import App, ComposeResult
from textual.widgets import Static


class CenterApp(App):
    """How to center things."""

    CSS = """
    Screen {
        align: center middle;
    }

    .words {
        background: blue 50%;
        border: wide white;
        width: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("How about a nice game", classes="words")
        yield Static("of chess?", classes="words")


if __name__ == "__main__":
    app = CenterApp()
    app.run()
