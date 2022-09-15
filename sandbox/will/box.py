from textual.app import App
from textual.widgets import Static

class BoxApp(App):

    def compose(self):
        yield Static("0123456789", id="box1")
        yield Static("0123456789", id="box2")
        yield Static("0123456789", id="box3")


app = BoxApp(css_path="box.css")
app.run()
