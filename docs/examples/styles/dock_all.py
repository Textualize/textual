from textual.app import App
from textual.containers import Container
from textual.widgets import Label


class DockAllApp(App):
    def compose(self):
        yield Container(
            Container(Label("left"), id="left"),
            Container(Label("top"), id="top"),
            Container(Label("right"), id="right"),
            Container(Label("bottom"), id="bottom"),
            id="big_container",
        )


app = DockAllApp(css_path="dock_all.css")
