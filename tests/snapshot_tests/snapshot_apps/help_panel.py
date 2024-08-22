from textual.app import App, ComposeResult
from textual.widgets import Input


class HelpPanelApp(App):
    def compose(self) -> ComposeResult:
        yield Input()


if __name__ == "__main__":
    app = HelpPanelApp()
    app.run()
