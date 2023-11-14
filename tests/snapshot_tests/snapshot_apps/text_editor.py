"""Tests the rendering of the TextEditor for all supported languages."""
from textual.app import App, ComposeResult
from textual.widgets import TextEditor


class TextAreaSnapshot(App):
    def compose(self) -> ComposeResult:
        text_editor = TextEditor()
        text_editor.cursor_blink = False
        yield text_editor


app = TextAreaSnapshot()
if __name__ == "__main__":
    app.run()
