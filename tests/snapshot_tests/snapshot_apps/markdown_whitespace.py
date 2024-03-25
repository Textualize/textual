from textual.app import App, ComposeResult
from textual.containers import Horizontal
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
    Markdown {
        margin-left: 0;
        border-left: solid red;
        width: 1fr;
        height: 1fr;
    }
    .code {
        height: 2fr;
        border-top: solid red;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal():
            for document in MARKDOWN:
                yield Markdown(document)
        yield Markdown("""```python
# Two spaces:  see?
class  Foo:
    '''This is    a doc    string.'''
    some_code(1,  2,   3,      4)
```
""", classes="code")

if __name__ == "__main__":
    MarkdownSpaceApp().run()
