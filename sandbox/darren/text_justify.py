from __future__ import annotations

from rich.text import Text

from textual.app import App, ComposeResult
from textual.widgets import Static

TEXT = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain."""


class TextJustify(App):
    def compose(self) -> ComposeResult:
        left = Static(Text(TEXT))
        left.styles.text_justify = "left"
        yield left

        right = Static(TEXT)
        right.styles.text_justify = "right"
        yield right

        center = Static(TEXT)
        center.styles.text_justify = "center"
        yield center

        full = Static(TEXT)
        full.styles.text_justify = "full"
        yield full


app = TextJustify(css_path="text_justify.scss", watch_css=True)

if __name__ == "__main__":
    app.run()
