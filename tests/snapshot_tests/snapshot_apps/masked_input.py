from textual.app import App, ComposeResult
from textual.widgets import MaskedInput


class TemplateApp(App[None]):
    def compose(self) -> ComposeResult:
        yield MaskedInput(">NNNNN-NNNNN-NNNNN-NNNNN;_")
        yield MaskedInput("9999-99-99", placeholder="YYYY-MM-DD")


if __name__ == "__main__":
    app = TemplateApp()
    app.run()