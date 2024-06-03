from textual.app import App, ComposeResult
from textual.widgets import Input


class TemplateApp(App[None]):
    def compose(self) -> ComposeResult:
        yield Input(template=">NNNNN-NNNNN-NNNNN-NNNNN;_")
        yield Input(template="9999-99-99", placeholder="YYYY-MM-DD")


if __name__ == "__main__":
    app = TemplateApp()
    app.run()
