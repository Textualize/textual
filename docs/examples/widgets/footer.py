from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer


class FooterApp(App):
    BINDINGS = [Binding(key="q", action="quit", description="Quit the app")]

    def compose(self) -> ComposeResult:
        yield Footer()


if __name__ == "__main__":
    app = FooterApp()
    app.run()
