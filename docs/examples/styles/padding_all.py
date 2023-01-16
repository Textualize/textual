from textual.app import App
from textual.containers import Container, Grid
from textual.widgets import Placeholder


class PaddingAllApp(App):
    def compose(self):
        yield Grid(
            Placeholder("no padding", id="p1"),
            Placeholder("padding: 1", id="p2"),
            Placeholder("padding: 1 5", id="p3"),
            Placeholder("padding: 1 1 2 6", id="p4"),
            Placeholder("padding-top: 4", id="p5"),
            Placeholder("padding-right: 3", id="p6"),
            Placeholder("padding-bottom: 4", id="p7"),
            Placeholder("padding-left: 3", id="p8"),
        )


app = PaddingAllApp(css_path="padding_all.css")
