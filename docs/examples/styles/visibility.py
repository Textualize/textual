from textual.app import App
from textual.widgets import Label


class VisibilityApp(App):
    def compose(self):
        yield Label("Widget 1")
        yield Label("Widget 2", classes="invisible")
        yield Label("Widget 3")


app = VisibilityApp(css_path="visibility.css")
