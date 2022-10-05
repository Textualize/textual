from textual.app import App
from textual.containers import Container
from textual.widgets import Static


class LayoutApp(App):
    def compose(self):
        yield Container(
            Static("Layout"),
            Static("Is"),
            Static("Vertical"),
            id="vertical-layout",
        )
        yield Container(
            Static("Layout"),
            Static("Is"),
            Static("Horizontal"),
            id="horizontal-layout",
        )


app = LayoutApp(css_path="layout.css")
