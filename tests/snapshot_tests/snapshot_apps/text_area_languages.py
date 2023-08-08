"""Tests the rendering of the TextArea for all supported languages."""
from textual.app import App, ComposeResult
from textual.widgets import TextArea


class TextAreaSnapshot(App):
    def compose(self) -> ComposeResult:
        yield TextArea()


app = TextAreaSnapshot()
if __name__ == "__main__":
    app.run()
