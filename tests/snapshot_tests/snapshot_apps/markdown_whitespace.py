from textual.app import App, ComposeResult
from textual.widgets import Markdown

MARKDOWN = (
    """\
X X

X  X

X\tX

X\t\tX
""",
    """\
X \tX

X \t \tX
""",
    """\
[X X  X\tX\t\tX \t \tX](https://example.com/)

_X X  X\tX\t\tX \t \tX_

**X X  X\tX\t\tX \t \tX**

~~X X  X\tX\t\tX \t \tX~~
"""
)

class MarkdownSpaceApp(App[None]):

    CSS = """
    Screen {
        layout: horizontal;
    }
    Markdown {
        margin-left: 0;
        border-left: solid red;
        width: 1fr;
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        for document in MARKDOWN:
            yield Markdown(document)

if __name__ == "__main__":
    MarkdownSpaceApp().run()
