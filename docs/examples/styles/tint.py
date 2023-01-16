from textual.app import App
from textual.color import Color
from textual.widgets import Label


class TintApp(App):
    def compose(self):
        color = Color.parse("green")
        for tint_alpha in range(0, 101, 10):
            widget = Label(f"tint: green {tint_alpha}%;")
            widget.styles.tint = color.with_alpha(tint_alpha / 100)  # (1)!
            yield widget


app = TintApp(css_path="tint.css")
