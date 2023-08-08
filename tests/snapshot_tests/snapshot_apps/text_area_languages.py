"""Tests the rendering of the TextArea for all supported languages."""
from textual.app import App, ComposeResult
from textual.widgets import TextArea


class TextAreaSnapshot(App):
    # def __init__(self, language: str, content: str) -> None:
    #     super().__init__()
    #     self.language = language
    #     self.content = content

    def compose(self) -> ComposeResult:
        yield TextArea()


app = TextAreaSnapshot()
if __name__ == "__main__":
    app.run()
