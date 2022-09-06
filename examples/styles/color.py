from textual.app import App
from textual.widgets import Static


class ColorApp(App):
    def compose(self):
        yield Static("I'm red!", id="static1")
        yield Static("I'm rgb(0, 255, 0)!", id="static2")
        yield Static("I'm hsl(240, 100%, 50%)!", id="static3")


app = ColorApp(css_path="color.css")
