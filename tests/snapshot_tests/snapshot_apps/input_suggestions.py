from textual.app import App, ComposeResult
from textual.widgets import Input


fruits = ["apple", "pear", "mango", "peach", "strawberry", "blueberry", "banana"]


class FruitsApp(App[None]):
    CSS = """
    Input > .input--suggestion {
        color: red;
        text-style: italic;
    }
    """

    def compose(self) -> ComposeResult:
        yield Input("straw", suggestions=fruits)


if __name__ == "__main__":
    app = FruitsApp()
    app.run()
