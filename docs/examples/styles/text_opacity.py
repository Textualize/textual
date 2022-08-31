from textual.app import App
from textual.widgets import Static


class TextOpacityApp(App):
    def compose(self):
        yield Static("text-opacity: 0%", id="zero-opacity")
        yield Static("text-opacity: 25%", id="quarter-opacity")
        yield Static("text-opacity: 50%", id="half-opacity")
        yield Static("text-opacity: 75%", id="three-quarter-opacity")
        yield Static("text-opacity: 100%", id="full-opacity")


app = TextOpacityApp(css_path="text_opacity.css")
