from textual.app import App
from textual.widgets import Static


class SpacingApp(App):
    def compose(self):
        yield Static(id="2332")


app = SpacingApp(css_path="spacing.css")
