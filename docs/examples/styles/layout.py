from textual.app import App
from textual.containers import Container
from textual.widgets import Label


class LayoutApp(App):
    def compose(self):
        yield Container(
            Label("Layout"),
            Label("Is"),
            Label("Vertical"),
            id="vertical-layout",
        )
        yield Container(
            Label("Layout"),
            Label("Is"),
            Label("Horizontal"),
            id="horizontal-layout",
        )


app = LayoutApp(css_path="layout.css")
