from textual.app import App, ComposeResult
from textual.widgets import Static


class CenterLayoutExample(App):
    def compose(self) -> ComposeResult:
        yield Static("Three", id="top")
        yield Static("Two", id="middle")
        yield Static("One", id="bottom")


app = CenterLayoutExample(css_path="center_layout.css")
if __name__ == "__main__":
    app.run()
