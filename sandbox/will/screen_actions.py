from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Footer


class DefaultScreen(Screen):

    BINDINGS = [("f", "foo", "FOO")]

    def compose(self) -> ComposeResult:
        yield Footer()

    def action_foo(self) -> None:
        self.app.bell()


class ScreenApp(App):
    def on_mount(self) -> None:
        self.push_screen(DefaultScreen())


app = ScreenApp()
if __name__ == "__main__":
    app.run()
