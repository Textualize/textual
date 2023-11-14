"""Tests the rendering of the TextArea for all supported languages."""
from textual.app import App, ComposeResult
from textual.widgets import TextEditor


class TextAreaUnfocusSnapshot(App):
    AUTO_FOCUS = None

    def compose(self) -> ComposeResult:
        text_editor = TextEditor()
        text_editor.cursor_blink = False
        yield text_editor


app = TextAreaUnfocusSnapshot()
if __name__ == "__main__":
    app.run()
