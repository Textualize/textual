from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Label, Static


class Box(Static):
    DEFAULT_CSS = """    
    Box {
        border: solid white;
        background: darkblue;
        width: 16;
        height: auto;
    }    
    """

    def compose(self) -> ComposeResult:
        yield Label("FOO\nBAR\nBAZ")


class OffsetsApp(App):

    CSS = """
    
    #box1 {
        offset: 5 5;
    }

    #box2 {
        offset: 15 10;
    }    
    
    """

    def compose(self) -> ComposeResult:
        yield Box(id="box1")
        yield Box(id="box2")


if __name__ == "__main__":
    app = OffsetsApp()
    app.run()
