from textual.app import App
from textual.containers import Horizontal, Container
from textual.widgets import Label

TEXT = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain.
"""


class ScrollbarApp(App):
    def compose(self):
        yield Horizontal(
            Container(Label(TEXT * 10)),
            Container(Label(TEXT * 10), classes="right"),
        )


app = ScrollbarApp(css_path="scrollbars.css")
