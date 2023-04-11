from textual.app import App, ComposeResult
from textual.widgets import Label
from textual.containers import Container


# Test fr dimensions and margins work in an auto container
# https://github.com/Textualize/textual/issues/2220
class TestApp(App):
    CSS = """
    Container {
        background: green 20%;
        border: heavy green;
        width: auto;
        height: auto;
        overflow: hidden;
    }

    Label {
        background: green 20%;      
        width: 1fr;
        height: 1fr;
        margin: 2 2;            
    }
    """

    def compose(self) -> ComposeResult:
        with Container():
            yield Label("Hello")
            yield Label("World")
            yield Label("!!")


if __name__ == "__main__":
    app = TestApp()
    app.run()
