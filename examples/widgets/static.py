from textual.app import App, ComposeResult
from textual.widgets import Static


class StaticApp(App):
    def compose(self) -> ComposeResult:
        yield Static("Hello, world!")


if __name__ == "__main__":
    app = StaticApp()
    app.run()
