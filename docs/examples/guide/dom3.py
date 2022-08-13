from textual.app import App, ComposeResult
from textual.layout import Container
from textual.widgets import Header, Footer, Static


class ExampleApp(App):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Container(
            Static(id="widget1"),
            Static(id="widget2"),
            Static(id="widget3"),
        )


app = ExampleApp()
