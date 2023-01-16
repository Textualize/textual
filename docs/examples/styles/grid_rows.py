from textual.app import App
from textual.containers import Grid
from textual.widgets import Label


class MyApp(App):
    def compose(self):
        yield Grid(
            Label("1fr"),
            Label("1fr"),
            Label("height = 6"),
            Label("height = 6"),
            Label("25%"),
            Label("25%"),
            Label("1fr"),
            Label("1fr"),
            Label("height = 6"),
            Label("height = 6"),
        )


app = MyApp(css_path="grid_rows.css")
