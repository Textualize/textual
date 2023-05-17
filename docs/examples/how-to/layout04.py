from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll
from textual.screen import Screen
from textual.widgets import Placeholder


class Header(Placeholder):
    DEFAULT_CSS = """
    Header {
        height: 3;
        dock: top;
    }
    """


class Footer(Placeholder):
    DEFAULT_CSS = """
    Footer {
        height: 3;
        dock: bottom;
    }
    """


class TweetScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(id="Header")
        yield Footer(id="Footer")
        yield HorizontalScroll()  # (1)!


class LayoutApp(App):
    def on_ready(self) -> None:
        self.push_screen(TweetScreen())


if __name__ == "__main__":
    app = LayoutApp()
    app.run()
