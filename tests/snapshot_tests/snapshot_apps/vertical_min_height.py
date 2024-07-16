from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Placeholder


class VerticalApp(App):
    CSS = """
    #top {
        min-height: 10;        
        height: 1fr;
        border: white;
    }
    #bottom {
        height:3fr;
        border: white;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Placeholder(id="top")
            yield Placeholder(id="bottom")


if __name__ == "__main__":
    VerticalApp().run()
