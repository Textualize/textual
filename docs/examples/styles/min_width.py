from textual.app import App
from textual.containers import Vertical
from textual.widgets import Placeholder


class MinWidthApp(App):
    def compose(self):
        yield Vertical(
            Placeholder("min-width: 25%", id="p1"),
            Placeholder("min-width: 75%", id="p2"),
            Placeholder("min-width: 100", id="p3"),
            Placeholder("min-width: 400h", id="p4"),
        )


app = MinWidthApp(css_path="min_width.css")
