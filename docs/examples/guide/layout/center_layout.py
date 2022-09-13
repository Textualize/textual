from textual.app import App, ComposeResult
from textual.widgets import Static


class CenterLayoutExample(App):
    def compose(self) -> ComposeResult:
        yield Static("One", id="bottom")
        yield Static("Two", id="middle")
        yield Static("Three", id="top")


app = CenterLayoutExample(css_path="center_layout.css")
if __name__ == "__main__":
    app.run()
