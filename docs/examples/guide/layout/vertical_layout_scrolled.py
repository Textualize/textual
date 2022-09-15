from textual.app import App, ComposeResult
from textual.widgets import Static


class VerticalLayoutScrolledExample(App):
    def compose(self) -> ComposeResult:
        yield Static("One", classes="box")
        yield Static("Two", classes="box")
        yield Static("Three", classes="box")


app = VerticalLayoutScrolledExample(css_path="vertical_layout_scrolled.css")
if __name__ == "__main__":
    app.run()
