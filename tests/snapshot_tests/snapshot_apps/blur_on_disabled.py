from textual.app import App, ComposeResult
from textual.widgets import Input


class BlurApp(App):
    BINDINGS = [("f3", "disable")]

    def compose(self) -> ComposeResult:
        yield Input()

    def on_ready(self) -> None:
        self.query_one(Input).focus()

    def action_disable(self) -> None:
        self.query_one(Input).disabled = True


if __name__ == "__main__":
    app = BlurApp()
    app.run()
