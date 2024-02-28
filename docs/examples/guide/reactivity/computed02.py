from textual.app import App, ComposeResult
from textual.color import Color
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import Input, Static


class ComputedApp(App):
    CSS_PATH = "computed01.tcss"

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

    @color.compute  # (1)!
    def _(self) -> Color:
        return Color(self.red, self.green, self.blue).clamped

    @color.watch  # (2)!
    def _(self, color: Color) -> None:
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
