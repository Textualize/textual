from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Markdown

CSS_PATH = (Path(__file__) / "../markdown_component_classes_reloading.tcss").resolve()

CSS_PATH.write_text(
    """\
.code_inline,
.em,
.strong,
.s,
.markdown-table--header,
.markdown-table--lines,
{
    color: yellow;
}
"""
)

MD = """
# This is a **header**

| col1 | col2 |
| :- | :- |
| value 1 | value 2 |

Here's some code: `from itertools import product`.
**Bold text**
_Emphasized text_
~~strikethrough~~

```py
print("Hello, world!")
```

**That** was _some_ code.
"""


class MyApp(App[None]):
    CSS_PATH = CSS_PATH

    def compose(self) -> ComposeResult:
        yield Markdown(MD)


if __name__ == "__main__":
    MyApp().run()
