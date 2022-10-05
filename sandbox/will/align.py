from textual.app import App, ComposeResult
from textual.widgets import Static


class Label(Static):
    pass


class AlignApp(App):
    CSS_PATH = "align.css"

    def compose(self) -> ComposeResult:
        yield Label("Hello")
        yield Label("World!")


if __name__ == "__main__":
    app = AlignApp()
    app.run()
