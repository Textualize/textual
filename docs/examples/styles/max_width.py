from textual.app import App
from textual.containers import Vertical
from textual.widgets import Placeholder


class MaxWidthApp(App):
    def compose(self):
        yield Vertical(
            Placeholder("max-width: 50h", id="p1"),
            Placeholder("max-width: 999", id="p2"),
            Placeholder("max-width: 50%", id="p3"),
            Placeholder("max-width: 30", id="p4"),
        )


app = MaxWidthApp(css_path="max_width.css")
