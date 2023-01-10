from textual.app import App
from textual.containers import Horizontal
from textual.widgets import Placeholder


class MinHeightApp(App):
    def compose(self):
        yield Horizontal(
            Placeholder("min-height: 25%", id="p1"),
            Placeholder("min-height: 75%", id="p2"),
            Placeholder("min-height: 30", id="p3"),
            Placeholder("min-height: 40w", id="p4"),
        )


app = MinHeightApp(css_path="min_height.css")
