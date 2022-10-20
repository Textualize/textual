from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.color import Color
from textual.widgets import Static

START_COLOR = Color.parse("#FF0000EE")
END_COLOR = Color.parse("#0000FF0F")


class ColorAnimate(App):
    BINDINGS = [Binding("d", action="toggle_dark", description="Dark mode")]

    def compose(self) -> ComposeResult:
        self.box = Static("Hello, world", id="box")
        self.box.styles.background = START_COLOR

        self.another_box = Static("Another box with $boost", id="another-box")

        yield self.box
        yield self.another_box

    def key_a(self):
        self.animator.animate(self.box.styles, "background", END_COLOR, duration=2.0)


app = ColorAnimate(css_path="color_animate.css")
if __name__ == "__main__":
    app.run()
