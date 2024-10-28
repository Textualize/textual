from textual.app import App, ComposeResult
from textual.widgets import Link


class LabelApp(App):
    AUTO_FOCUS = None
    CSS = """
    Screen {
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        yield Link(
            "Go to textualize.io",
            url="https://textualize.io",
            tooltip="Click me",
        )


if __name__ == "__main__":
    app = LabelApp()
    app.run()
