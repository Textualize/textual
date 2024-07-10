from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Container
from textual.widgets import Button


class ScrollVisibleMargin(App):
    CSS = """
    Container {
        height: auto;
        margin-top: 8;
        border: solid red;
    }
    """

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            with Container():
                for index in range(1, 51):
                    yield Button(f"Hello, world! ({index})", id=f"b{index}")

    def key_x(self):
        button_twenty = self.query_one("#b26")
        button_twenty.scroll_visible()


app = ScrollVisibleMargin()
if __name__ == "__main__":
    app.run()
