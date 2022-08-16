from textual.app import App, ComposeResult
from textual.widgets import Static


class FillApp(App):
    def compose(self) -> ComposeResult:
        yield Static("Hello")


app = FillApp(css_path="fill.css")
