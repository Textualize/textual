from textual.app import App, ComposeResult
from textual.widgets import TextEditor
from textual.widgets.text_editor import Selection

TEXT = """\
def hello(name):
    print("hello" + name)

def goodbye(name):
    print("goodbye" + name)
"""


class TextAreaSelection(App):
    def compose(self) -> ComposeResult:
        text_editor = TextEditor(TEXT, language="python")
        text_editor.selection = Selection(start=(0, 0), end=(2, 0))  # (1)!
        yield text_editor


app = TextAreaSelection()
if __name__ == "__main__":
    app.run()
