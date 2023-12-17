from textual.app import App, ComposeResult
from textual.widgets import Static


class TestApp(App):
    DEFAULT_CSS = """
    Screen {
        scrollbar-size: 0 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("Hello, world!\n" * 100)


if __name__ == "__main__":
    TestApp().run()
