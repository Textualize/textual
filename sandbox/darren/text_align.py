from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Static

TEXT = (
    "I must not fear. Fear is the mind-killer. Fear is the little-death that "
    "brings total obliteration. I will face my fear. I will permit it to pass over "
    "me and through me. And when it has gone past, I will turn the inner eye to "
    "see its path. Where the fear has gone there will be nothing. Only I will "
    "remain. "
)


class TextAlign(App):
    def compose(self) -> ComposeResult:
        left = Static("[b]Left aligned[/]\n" + TEXT, id="one")
        yield left

        right = Static("[b]Center aligned[/]\n" + TEXT, id="two")
        yield right

        center = Static("[b]Right aligned[/]\n" + TEXT, id="three")
        yield center

        full = Static("[b]Fully justified[/]\n" + TEXT, id="four")
        yield full


app = TextAlign(css_path="text_align.scss", watch_css=True)

if __name__ == "__main__":
    app.run()
