from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button


class HorizontalWidthAutoApp(App[None]):
    CSS = """
    Horizontal {
        border: solid red;
        height: auto;
        width: auto;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal(classes="auto"):
            yield Button("This is a very wide button")

        with Horizontal(classes="auto"):
            yield Button("This is a very wide button")
            yield Button("This is a very wide button")


if __name__ == "__main__":
    HorizontalWidthAutoApp().run()
