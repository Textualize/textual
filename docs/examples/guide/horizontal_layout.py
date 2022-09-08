from textual.app import App, ComposeResult
from textual.widgets import Static


class HorizontalLayoutExample(App):
    def compose(self) -> ComposeResult:
        yield Static("One", classes="box")
        yield Static("Two", classes="box")
        yield Static("Three", classes="box")


app = HorizontalLayoutExample(css_path="horizontal_layout.css")
if __name__ == "__main__":
    app.run()
