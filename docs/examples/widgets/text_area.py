from textual.app import App, ComposeResult
from textual.widgets import TextArea

TEXT = """\
def hello(name):
    print("hello" + name)

def goodbye(name):
    print("goodbye" + name)
"""


class TextAreaSelection(App):
    def compose(self) -> ComposeResult:
        yield TextArea(TEXT, language="python")


app = TextAreaSelection()
if __name__ == "__main__":
    app.run()
