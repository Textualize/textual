from textual.app import App, ComposeResult
from textual.widgets import LoadingIndicator


class LoadingApp(App):
    def compose(self) -> ComposeResult:
        yield LoadingIndicator()


if __name__ == "__main__":
    app = LoadingApp()
    app.run()
