from textual.app import App, ComposeResult
from textual.widgets import Label, Input
from textual.containers import Container


class GridApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    Container {
        layout: grid;
        grid-size: 2;
        grid-columns: auto 1fr;
        grid-rows: auto;
        height:auto;
        border: solid green;
    }
    
    #c2 Label {
        min-width: 20;
    }

    #c3 Label {
        max-width: 30;
    }

    """

    AUTO_FOCUS = None

    def compose(self) -> ComposeResult:
        with Container(id="c1"):
            yield Label("foo")
            yield Input()
            yield Label("Longer label")
            yield Input()
        with Container(id="c2"):
            yield Label("foo")
            yield Input()
            yield Label("Longer label")
            yield Input()
        with Container(id="c3"):
            yield Label("foo bar " * 10)
            yield Input()
            yield Label("Longer label")
            yield Input()


if __name__ == "__main__":
    app = GridApp()
    app.run()
