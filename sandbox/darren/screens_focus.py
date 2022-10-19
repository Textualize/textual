from textual.app import App, ComposeResult, ScreenStackError
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Static, Footer, Input

from some_text import TEXT


class Focusable(Static, can_focus=True):
    pass


class CustomScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Focusable(f"Screen {id(self)} - two {TEXT}")
        yield Focusable(f"Screen {id(self)} - three")
        yield Focusable(f"Screen {id(self)} - four")
        yield Input(placeholder="Text input")
        yield Footer()


class MyInstalledScreen(Screen):
    def __init__(self, string: str):
        super().__init__()
        self.string = string

    def compose(self) -> ComposeResult:
        yield Static(f"Hello, world! {self.string}")


class ScreensFocusApp(App):
    BINDINGS = [
        Binding("plus", "push_new_screen", "Push"),
        Binding("minus", "pop_top_screen", "Pop"),
        Binding("d", "toggle_dark", "Toggle Dark"),
        Binding("q", "push_screen('q')", "Screen Q"),
        Binding("w", "push_screen('w')", "Screen W"),
        Binding("e", "push_screen('e')", "Screen E"),
        Binding("r", "push_screen('r')", "Screen R"),
    ]

    SCREENS = {
        "q": MyInstalledScreen("q"),
        "w": MyInstalledScreen("w"),
        "e": MyInstalledScreen("e"),
        "r": MyInstalledScreen("r"),
    }

    def compose(self) -> ComposeResult:
        yield Focusable("App - one")
        yield Input(placeholder="Text input")
        yield Input(placeholder="Text input")
        yield Focusable("App - two")
        yield Focusable("App - three")
        yield Focusable("App - four")
        yield Footer()

    def action_push_new_screen(self):
        self.push_screen(CustomScreen())

    def action_pop_top_screen(self):
        try:
            self.pop_screen()
        except ScreenStackError:
            pass

    def _action_toggle_dark(self):
        self.dark = not self.dark


app = ScreensFocusApp(css_path="screens_focus.css")
if __name__ == "__main__":
    app.run()
