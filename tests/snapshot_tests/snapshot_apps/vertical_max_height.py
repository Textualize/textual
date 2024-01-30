from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Placeholder


class VerticalApp(App):
    CSS = """
    #top {        
        height: 1fr;
        border: white;
    }
    #bottom {
        height:3fr;
        border: white;
        max-height: 10;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Placeholder(id="top")
            yield Placeholder(id="bottom")


if __name__ == "__main__":
    VerticalApp().run()
