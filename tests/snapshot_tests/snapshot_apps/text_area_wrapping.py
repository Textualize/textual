from textual.app import App, ComposeResult
from textual.widgets import TextArea

TEXT = """\
# The Wonders of Space Exploration

Space exploration has *always* captured the human imagination.

ダレンバーンズ

\tThisissomelongtextthatshouldfoldcorrectly.

\t\tダレン バーンズ







"""


class TextAreaWrapping(App):
    def compose(self) -> ComposeResult:
        yield TextArea.code_editor(TEXT, language="markdown", theme="monokai", soft_wrap=True)


app = TextAreaWrapping()
if __name__ == "__main__":
    app.run()
