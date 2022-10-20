from textual.app import App, ComposeResult
from textual.color import Color
from textual.widgets import Static

START_COLOR = Color.parse("#FF0000EE")
END_COLOR = Color.parse("#0000FF0F")


class ColorAnimate(App):
    def compose(self) -> ComposeResult:
        box = Static("Hello, world", id="box")
        box.styles.background = START_COLOR
        self.box = box
        yield box

    def key_a(self):
        self.animator.animate(self.box.styles, "background", END_COLOR, duration=2.0)


app = ColorAnimate(css_path="color_animate.css")
if __name__ == "__main__":
    app.run()
