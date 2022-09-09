from textual.app import App, ComposeResult
from textual.widgets import Static


class VerticalLayoutExample(App):
    def compose(self) -> ComposeResult:
        yield Static("One", classes="box")
        yield Static("Two", classes="box")
        yield Static("Three", classes="box")


app = VerticalLayoutExample(css_path="vertical_layout.css")
if __name__ == "__main__":
    app.run()
