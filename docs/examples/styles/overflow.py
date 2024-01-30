from textual.app import App
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Static

TEXT = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain."""


class OverflowApp(App):
    CSS_PATH = "overflow.tcss"

    def compose(self):
        yield Horizontal(
            VerticalScroll(Static(TEXT), Static(TEXT), Static(TEXT), id="left"),
            VerticalScroll(Static(TEXT), Static(TEXT), Static(TEXT), id="right"),
        )


if __name__ == "__main__":
    app = OverflowApp()
    app.run()
