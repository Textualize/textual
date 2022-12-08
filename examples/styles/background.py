from textual.app import App
from textual.widgets import Static


class BackgroundApp(App):
    def compose(self):
        yield Static("Widget 1", id="static1")
        yield Static("Widget 2", id="static2")
        yield Static("Widget 3", id="static3")


app = BackgroundApp(css_path="background.css")
