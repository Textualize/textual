from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button


class WidgetDisableTestApp(App[None]):
    CSS = """
    Horizontal {
        height: auto;
    }

    Button {
        width: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        for _ in range(4):
            with Horizontal():
                yield Button()
                yield Button(variant="primary")
                yield Button(variant="success")
                yield Button(variant="warning")
                yield Button(variant="error")
            with Horizontal(disabled=True):
                yield Button()
                yield Button(variant="primary")
                yield Button(variant="success")
                yield Button(variant="warning")
                yield Button(variant="error")


if __name__ == "__main__":
    WidgetDisableTestApp().run()
