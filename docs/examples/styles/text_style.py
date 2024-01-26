from textual.app import App
from textual.widgets import Label

TEXT = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain."""


class TextStyleApp(App):
    CSS_PATH = "text_style.tcss"

    def compose(self):
        yield Label(TEXT, id="lbl1")
        yield Label(TEXT, id="lbl2")
        yield Label(TEXT, id="lbl3")


if __name__ == "__main__":
    app = TextStyleApp()
    app.run()
