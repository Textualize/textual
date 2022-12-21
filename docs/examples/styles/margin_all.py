from textual.app import App
from textual.containers import Container, Grid
from textual.widgets import Placeholder


class MarginAllApp(App):
    def compose(self):
        yield Grid(
            Container(Placeholder("no margin", id="p1"), classes="bordered"),
            Container(Placeholder("margin: 1", id="p2"), classes="bordered"),
            Container(Placeholder("margin: 1 5", id="p3"), classes="bordered"),
            Container(Placeholder("margin: 1 1 2 6", id="p4"), classes="bordered"),
            Container(Placeholder("margin-top: 4", id="p5"), classes="bordered"),
            Container(Placeholder("margin-right: 3", id="p6"), classes="bordered"),
            Container(Placeholder("margin-bottom: 4", id="p7"), classes="bordered"),
            Container(Placeholder("margin-left: 3", id="p8"), classes="bordered"),
        )


app = MarginAllApp(css_path="margin_all.css")
