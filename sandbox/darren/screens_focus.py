from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Static, Footer


class Focusable(Static, can_focus=True):
    pass


class CustomScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Focusable(f"Screen {id(self)} - one")
        yield Focusable(f"Screen {id(self)} - two")
        yield Focusable(f"Screen {id(self)} - three")
        yield Focusable(f"Screen {id(self)} - four")
        yield Footer()


class ScreensFocusApp(App):
    BINDINGS = [
        Binding("plus_sign", "push_new_screen", "Push"),
        Binding("hyphen_minus", "pop_top_screen", "Pop"),
    ]

    def compose(self) -> ComposeResult:
        yield Focusable("App - one")
        yield Focusable("App - two")
        yield Focusable("App - three")
        yield Focusable("App - four")
        yield Footer()

    def action_push_new_screen(self):
        self.push_screen(CustomScreen())

    def action_pop_top_screen(self):
        self.pop_screen()


app = ScreensFocusApp(css_path="screens_focus.css")
if __name__ == "__main__":
    app.run()
