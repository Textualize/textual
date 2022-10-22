from textual.app import App
from textual.widgets import Static


class VisibilityApp(App):
    def compose(self):
        yield Static("Widget 1")
        yield Static("Widget 2", classes="invisible")
        yield Static("Widget 3")


app = VisibilityApp(css_path="visibility.css")
