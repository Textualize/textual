from textual.app import App
from textual.containers import Grid
from textual.widgets import Label

TEXT = (
    "I must not fear. Fear is the mind-killer. Fear is the little-death that "
    "brings total obliteration. I will face my fear. I will permit it to pass over "
    "me and through me."
)


class TextAlign(App):
    def compose(self):
        yield Grid(
            Label("[b]Left aligned[/]\n" + TEXT, id="one"),
            Label("[b]Center aligned[/]\n" + TEXT, id="two"),
            Label("[b]Right aligned[/]\n" + TEXT, id="three"),
            Label("[b]Justified[/]\n" + TEXT, id="four"),
        )


app = TextAlign(css_path="text_align.css")
