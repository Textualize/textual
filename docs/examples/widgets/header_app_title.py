from textual.app import App, ComposeResult
from textual.widgets import Header


class HeaderApp(App):
    def compose(self) -> ComposeResult:
        yield Header()

    def on_mount(self) -> None:
        self.title = "Header Application"
        self.sub_title = "With title and sub-title"


if __name__ == "__main__":
    app = HeaderApp()
    app.run()
