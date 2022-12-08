from textual.app import App
from textual.widgets import Static


class OpacityApp(App):
    def compose(self):
        yield Static("opacity: 0%", id="zero-opacity")
        yield Static("opacity: 25%", id="quarter-opacity")
        yield Static("opacity: 50%", id="half-opacity")
        yield Static("opacity: 75%", id="three-quarter-opacity")
        yield Static("opacity: 100%", id="full-opacity")


app = OpacityApp(css_path="opacity.css")
