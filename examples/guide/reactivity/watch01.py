from textual.app import App, ComposeResult
from textual.color import Color, ColorParseError
from textual.containers import Grid
from textual.reactive import reactive
from textual.widgets import Input, Static


class WatchApp(App):
    CSS_PATH = "watch01.css"

    color = reactive(Color.parse("transparent"))  # (1)!

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Enter a color")
        yield Grid(Static(id="old"), Static(id="new"), id="colors")

    def watch_color(self, old_color: Color, new_color: Color) -> None:  # (2)!
        self.query_one("#old").styles.background = old_color
        self.query_one("#new").styles.background = new_color

    def on_input_submitted(self, event: Input.Submitted) -> None:
        try:
            input_color = Color.parse(event.value)
        except ColorParseError:
            pass
        else:
            self.query_one(Input).value = ""
            self.color = input_color  # (3)!


if __name__ == "__main__":
    app = WatchApp()
    app.run()
