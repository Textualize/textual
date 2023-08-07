from textual.app import App, ComposeResult
from textual.widgets import Static

QUOTE = "Could not find you in Seattle and no terminal is in operation at your classified address."


class CenterApp(App):
    """How to center things."""

    CSS = """
    Screen {
        align: center middle;
    }

    #hello {
        background: blue 50%;
        border: wide white;
        width: 40;
        height: 9;
        text-align: center;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static(QUOTE, id="hello")


if __name__ == "__main__":
    app = CenterApp()
    app.run()
