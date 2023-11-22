from textual.app import App, ComposeResult
from textual.widgets import Input


class InputApp(App):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="An integer", type="integer")
        yield Input(placeholder="A number", type="number")


if __name__ == "__main__":
    app = InputApp()
    app.run()
