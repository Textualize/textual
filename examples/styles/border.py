from textual.app import App
from textual.widgets import Static


class BorderApp(App):
    def compose(self):
        yield Static("My border is solid red", id="static1")
        yield Static("My border is dashed green", id="static2")
        yield Static("My border is tall blue", id="static3")


app = BorderApp(css_path="border.css")
