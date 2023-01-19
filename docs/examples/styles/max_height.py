from textual.app import App
from textual.containers import Horizontal
from textual.widgets import Placeholder


class MaxHeightApp(App):
    def compose(self):
        yield Horizontal(
            Placeholder("max-height: 10w", id="p1"),
            Placeholder("max-height: 999", id="p2"),
            Placeholder("max-height: 50%", id="p3"),
            Placeholder("max-height: 10", id="p4"),
        )


app = MaxHeightApp(css_path="max_height.css")
