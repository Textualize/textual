from textual.app import App
from textual.widgets import Label


class OffsetApp(App):
    def compose(self):
        yield Label("Paul (offset 8 2)", classes="paul")
        yield Label("Duncan (offset 4 10)", classes="duncan")
        yield Label("Chani (offset 0 -3)", classes="chani")


app = OffsetApp(css_path="offset.css")
