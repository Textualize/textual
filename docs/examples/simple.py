from textual.app import App, ComposeResult
from textual.widgets import Static


class TextApp(App):
    def compose(self) -> ComposeResult:
        yield Static("Hello")
        yield Static("[b]World![/b]")


app = TextApp(css_path="simple.css")
