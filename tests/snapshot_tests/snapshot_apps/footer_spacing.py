from textual.app import App, ComposeResult
from textual.widgets import Footer


class FooterApp(App):
    CSS = """
    Footer > FooterKey .footer-key--key{
        background: red;
    }
    """
    BINDINGS = [("q", "quit", "Quit the app")]

    def compose(self) -> ComposeResult:
        yield Footer()


if __name__ == "__main__":
    app = FooterApp()
    app.run()
