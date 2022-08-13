from textual.app import App, ComposeResult
from textual.layout import Container
from textual.widget import Widget
from textual.widgets import Header, Footer


class ExampleApp(App):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Container(
            Widget(id="widget1"),
            Widget(id="widget2"),
            Widget(id="widget3"),
        )


app = ExampleApp()
