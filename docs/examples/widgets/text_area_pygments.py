from __future__ import annotations

from rich.syntax import Syntax
from rich.text import Text

from textual.app import App, ComposeResult
from textual.widgets import TextArea

TEXT = """\
def hello(name):
    print("hello" + name)

def goodbye(name):
    print("goodbye" + name)
"""


class TextAreaPygments(TextArea):
    def __init__(self, text: str = "", *, language: str = "python", **kwargs):
        super().__init__(text, language=None, **kwargs)
        self.syntax = Syntax("", lexer=language)

    def get_line(self, line_index: int) -> Text:
        line_str = self.document.get_line(line_index)
        # where the magic happens
        line = self.syntax.highlight(line_str)
        # by default, `.highlight` returns Text with `\n` appended
        line.remove_suffix("\n")

        line.expand_tabs(tab_size=4)
        # hack to remove highlighting of the preceding spaces if the code is indented
        spaces = 0
        if line.plain.startswith(" "):
            spaces_iter = iter(line)
            while next(spaces_iter) == " ":
                spaces += 1
        line = Text(" " * spaces, end="") + line[spaces:]

        return line


class TextAreaExample(App):
    def compose(self) -> ComposeResult:
        yield TextAreaPygments.code_editor(TEXT, language="python")


app = TextAreaExample()
if __name__ == "__main__":
    app.run()
