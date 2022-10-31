from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static


class StaticText(Static):
    pass


class Header(Static):
    pass


class Footer(Static):
    pass


class FrApp(App):

    CSS = """
    Screen {
        layout: horizontal;
        align: center middle;
      
    }

    Vertical {
        
    }

    Header {
        background: $boost;
        
        content-align: center middle;
        text-align: center;
        color: $text;
        height: 3;
        border: tall $warning;
    }

    Horizontal {
        height: 1fr;
        align: center middle;
    }

    Footer {
        background: $boost;
        
        content-align: center middle;
        text-align: center;
        
        color: $text;
        height: 6;
        border: tall $warning;
    }

    StaticText {
        background: $boost;
        height: 8;
        content-align: center middle;
        text-align: center;
        color: $text;
    }

    #foo {
        width: 10; 
        border: tall $primary;
    }

    #bar {
        width: 1fr;
        border: tall $error;
        
    }

    #baz {
        width: 20;
        border: tall $success;
    }

    """

    def compose(self) -> ComposeResult:
        yield Vertical(
            Header("HEADER"),
            Horizontal(
                StaticText("foo", id="foo"),
                StaticText("bar", id="bar"),
                StaticText("baz", id="baz"),
            ),
            Footer("FOOTER"),
        )


app = FrApp()
app.run()
