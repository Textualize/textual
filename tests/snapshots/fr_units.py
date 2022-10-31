from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static


class StaticText(Static):
    pass


class FRApp(App):

    CSS = """
    StaticText {
        height: 1fr;
        background: $boost;
        border: heavy white;
    }
    #foo {
        width: 10;
    }
    #bar {
        width: 1fr;
    }
    #baz {
        width: 8;
    }
    #header {
        height: 1fr
    }

    Horizontal {
        height: 2fr;
    }

    #footer {
        height: 4;
    }
    
    """

    def compose(self) -> ComposeResult:
        yield Vertical(
            StaticText("HEADER", id="header"),
            Horizontal(
                StaticText("foo", id="foo"),
                StaticText("bar", id="bar"),
                StaticText("baz", id="baz"),
            ),
            StaticText("FOOTER", id="footer"),
        )


if __name__ == "__main__":
    app = FRApp()
    app.run()
