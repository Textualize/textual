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

    """

    def compose(self) -> ComposeResult:
        with Container():
            yield Label("foo")
            yield Input()
            yield Label("Longer label")
            yield Input()


if __name__ == "__main__":
    app = GridApp()
    app.run()
