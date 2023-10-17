from textual.app import App, ComposeResult
from textual.widgets import Label


class BorderTitleApp(App):
    CSS_PATH = "border_title_colors.tcss"

    def compose(self) -> ComposeResult:
        yield Label("Hello, World!")

    def on_mount(self) -> None:
        label = self.query_one(Label)
        label.border_title = "Textual Rocks"
        label.border_subtitle = "Textual Rocks"


if __name__ == "__main__":
    app = BorderTitleApp()
    app.run()
