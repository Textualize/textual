from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Static

TEXT = (
    "I must not fear. Fear is the mind-killer. Fear is the little-death that "
    "brings total obliteration. I will face my fear. I will permit it to pass over "
    "me and through me."
)


class TextAlign(App):
    def compose(self) -> ComposeResult:
        left = Static("[b]Left aligned[/]\n" + TEXT, id="one")
        yield left

        right = Static("[b]Center aligned[/]\n" + TEXT, id="two")
        yield right

        center = Static("[b]Right aligned[/]\n" + TEXT, id="three")
        yield center

        full = Static("[b]Justified[/]\n" + TEXT, id="four")
        yield full


app = TextAlign(css_path="text_align.css")
