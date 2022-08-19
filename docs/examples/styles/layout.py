from textual import layout
from textual.app import App
from textual.widget import Widget
from textual.widgets import Static


class LayoutApp(App):
    def compose(self):
        yield layout.Container(
            Static("Layout"),
            Static("Is"),
            Static("Vertical"),
            id="vertical-layout",
        )
        yield layout.Container(
            Static("Layout"),
            Static("Is"),
            Static("Horizontal"),
            id="horizontal-layout",
        )
        yield layout.Container(
            Static("Center"),
            id="center-layout",
        )


app = LayoutApp(css_path="layout.css")
