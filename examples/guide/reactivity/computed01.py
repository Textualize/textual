from textual.app import App, ComposeResult
from textual.color import Color
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import Input, Static


class ComputedApp(App):
    CSS_PATH = "computed01.css"

    red = reactive(0)
    green = reactive(0)
    blue = reactive(0)
    color = reactive(Color.parse("transparent"))

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Input("0", placeholder="Enter red 0-255", id="red"),
            Input("0", placeholder="Enter green 0-255", id="green"),
            Input("0", placeholder="Enter blue 0-255", id="blue"),
            id="color-inputs",
        )
        yield Static(id="color")

    def compute_color(self) -> Color:  # (1)!
        return Color(self.red, self.green, self.blue).clamped

    def watch_color(self, color: Color) -> None:  # (2)
        self.query_one("#color").styles.background = color

    def on_input_changed(self, event: Input.Changed) -> None:
        try:
            component = int(event.value)
        except ValueError:
            self.bell()
        else:
            if event.input.id == "red":
                self.red = component
            elif event.input.id == "green":
                self.green = component
            else:
                self.blue = component


if __name__ == "__main__":
    app = ComputedApp()
    app.run()
