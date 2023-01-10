from textual.app import App
from textual.containers import Grid
from textual.widgets import Label


class MyApp(App):
    def compose(self):
        yield Grid(
            Label("1"),
            Label("2"),
            Label("3"),
            Label("4"),
            Label("5"),
        )


app = MyApp(css_path="grid_size_both.css")
