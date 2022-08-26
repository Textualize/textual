from textual.app import App
from textual.widgets import Static


class BoxSizingApp(App):
    def compose(self):
        yield Static("I'm using border-box!", id="static1")
        yield Static("I'm using content-box!", id="static2")


app = BoxSizingApp(css_path="box_sizing.css")
