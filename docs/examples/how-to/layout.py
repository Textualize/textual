from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, Vertical, VerticalScroll
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


class Tweet(Placeholder):
    DEFAULT_CSS = """
    Tweet {
        height: 5;
        width: 1fr;
        border: tall $background;
    }
    """


class ColumnsContainer(HorizontalScroll):
    pass


class Column(VerticalScroll):
    DEFAULT_CSS = """
    Column {
        height: 1fr;
        width: 32;
        margin: 0 2;

    }
    """

    def compose(self) -> ComposeResult:
        for tweet_no in range(1, 20):
            yield Tweet(id=f"Tweet{tweet_no}")


class TweetScreen(Screen):
    DEFAULT_CSS = """
    TweetScreen {
        layers: float;

    }
    """

    def compose(self) -> ComposeResult:
        yield Header(id="Header")
        yield Footer(id="Footer")
        with ColumnsContainer(id="Columns"):
            yield Column(id="Column1")
            yield Column(id="Column2")
            yield Column(id="Column3")
            yield Column(id="Column4")


class LayoutApp(App):
    CSS_PATH = "layout.css"

    def on_ready(self) -> None:
        self.push_screen(TweetScreen())


if __name__ == "__main__":
    app = LayoutApp()
    app.run()
