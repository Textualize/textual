"""Tests the rendering of the TextArea for all supported languages."""
from textual.app import App, ComposeResult
from textual.widgets import TextArea


class TextAreaUnfocusSnapshot(App):
    AUTO_FOCUS = None

    def compose(self) -> ComposeResult:
        text_area = TextArea.code_editor()
        text_area.cursor_blink = False
        yield text_area


app = TextAreaUnfocusSnapshot()
if __name__ == "__main__":
    app.run()
