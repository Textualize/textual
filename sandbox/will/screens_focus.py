from textual.app import App, ComposeResult
from textual.widgets import Static, Footer


class Focusable(Static, can_focus=True):
    pass


class ScreensFocusApp(App):
    def compose(self) -> ComposeResult:
        yield Focusable("App - one")
        yield Focusable("App - two")
        yield Focusable("App - three")
        yield Focusable("App - four")
        yield Footer()


app = ScreensFocusApp(css_path="screens_focus.css")
if __name__ == "__main__":
    app.run()
