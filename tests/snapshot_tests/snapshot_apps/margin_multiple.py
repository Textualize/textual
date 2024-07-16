from textual.app import App, ComposeResult
from textual.containers import Container, ScrollableContainer, Horizontal
from textual.widgets import Label


class CompoundWidget(ScrollableContainer):
    DEFAULT_CSS = """
    #inner {
        width: 1fr;
        background: $panel;
        align: center middle;
        margin: 5;
        border: green;
 
    }
    
    Label {
        border: double yellow;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("foo")
        with Container(id="inner"):
            yield Label("bar")


class MyApp(App):
    CSS = """
    #widget2 > Label {
        display: none;
    }

    """

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield CompoundWidget(id="widget1")
            yield CompoundWidget(id="widget2")


if __name__ == "__main__":
    MyApp().run()
