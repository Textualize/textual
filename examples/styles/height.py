from textual.app import App
from textual.widget import Widget


class HeightApp(App):
    def compose(self):
        yield Widget()


app = HeightApp(css_path="height.css")
