from textual.app import App
from textual.widgets import Static


class Clickable(Static):
    def on_click(self):
        self.app.bell()


class SpacingApp(App):
    def compose(self):
        yield Clickable()


app = SpacingApp(css_path="spacing.css")
