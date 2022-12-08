from textual.app import App
from textual.widgets import Static


class DisplayApp(App):
    def compose(self):
        yield Static("Widget 1")
        yield Static("Widget 2", classes="remove")
        yield Static("Widget 3")


app = DisplayApp(css_path="display.css")
