from textual.app import App
from textual.containers import Grid
from textual.widgets import Placeholder


class MyApp(App):
    def compose(self):
        yield Grid(
            Placeholder(id="p1"),
            Placeholder(id="p2"),
            Placeholder(id="p3"),
            Placeholder(id="p4"),
            Placeholder(id="p5"),
            Placeholder(id="p6"),
            Placeholder(id="p7"),
        )


app = MyApp(css_path="column_span.css")
