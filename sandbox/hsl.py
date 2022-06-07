from textual.app import App, ComposeResult
from textual.widgets import Static


class HSLApp(App):
    def compose(self) -> ComposeResult:
        yield Static(classes="box")


app = HSLApp(css_path="hsl.scss", watch_css=True)
app.run()
