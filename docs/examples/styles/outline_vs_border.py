from textual.app import App
from textual.widgets import Label

TEXT = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain."""


class OutlineBorderApp(App):
    CSS_PATH = "outline_vs_border.tcss"

    def compose(self):
        yield Label(TEXT, classes="outline")
        yield Label(TEXT, classes="border")
        yield Label(TEXT, classes="outline border")


if __name__ == "__main__":
    app = OutlineBorderApp()
    app.run()
