from textual.app import App
from textual.widget import Widget


class WidthApp(App):
    def compose(self):
        yield Widget()


app = WidthApp(css_path="width.css")
