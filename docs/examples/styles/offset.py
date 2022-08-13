from textual.app import App
from textual.widgets import Static


class OffsetApp(App):
    def compose(self):
        yield Static("Paul (offset 8 2)", classes="paul")
        yield Static("Duncan (offset 4 10)", classes="duncan")
        yield Static("Chani (offset 0 5)", classes="chani")


app = OffsetApp(css_path="offset.css")
