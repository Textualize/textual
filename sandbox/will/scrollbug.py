from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer


class ScrollApp(App):

    BINDINGS = [("q", "quit", "QUIT")]
    CSS_PATH = "scrollbug.css"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(id="test")
        yield Footer()


app = ScrollApp()
if __name__ == "__main__":
    app.run()
