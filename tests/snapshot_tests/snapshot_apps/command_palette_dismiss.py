from textual.app import App, ComposeResult
from textual.widgets import Label


class CPApp(App):
    def compose(self) -> ComposeResult:
        yield Label("Command palette test app")


if __name__ == "__main__":
    app = CPApp()
    app.run()
