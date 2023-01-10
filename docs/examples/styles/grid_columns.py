from textual.app import App
from textual.containers import Grid
from textual.widgets import Label


class MyApp(App):
    def compose(self):
        yield Grid(
            Label("1fr"),
            Label("width = 16"),
            Label("2fr"),
            Label("1fr"),
            Label("width = 16"),
            Label("1fr"),
            Label("width = 16"),
            Label("2fr"),
            Label("1fr"),
            Label("width = 16"),
        )


app = MyApp(css_path="grid_columns.css")
