from textual.app import App, ComposeResult
from textual.widgets import TextLog


class TextLogApp(App):
    def compose(self) -> ComposeResult:
        yield TextLog()

    def on_mount(self) -> None:
        tl = self.query_one(TextLog)
        tl.write("Hello")
        tl.write("")
        tl.write("World")


if __name__ == "__main__":
    app = TextLogApp()
    app.run()
