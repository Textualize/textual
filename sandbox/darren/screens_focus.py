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
        # yield Footer()


class ScreensFocusApp(App):
    BINDINGS = [
        Binding("plus", "push_new_screen", "Push"),
        Binding("minus", "pop_top_screen", "Pop"),
    ]

    def compose(self) -> ComposeResult:
        yield Focusable("App - one")
        yield Input(placeholder="Text input")
        yield Input(placeholder="Text input")
        yield Focusable("App - two")
        yield Focusable("App - three")
        yield Focusable("App - four")
        # yield Footer()

    def action_push_new_screen(self):
        self.push_screen(CustomScreen())

    def action_pop_top_screen(self):
        try:
            self.pop_screen()
        except ScreenStackError:
            pass


app = ScreensFocusApp(css_path="screens_focus.css")
if __name__ == "__main__":
    app.run()
