from textual.app import App, ComposeResult
from textual.widgets import Label


class LabelApp(App):
    def compose(self) -> ComposeResult:
        yield Label("Hello, world!")


if __name__ == "__main__":
    app = LabelApp()
    app.run()
