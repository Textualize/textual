from textual.app import App, ComposeResult
from textual.widgets import RichLog


class RichLogApp(App):
    def compose(self) -> ComposeResult:
        yield RichLog()

    def on_mount(self) -> None:
        tl = self.query_one(RichLog)
        tl.write("Hello")
        tl.write("")
        tl.write("World")


if __name__ == "__main__":
    app = RichLogApp()
    app.run()
