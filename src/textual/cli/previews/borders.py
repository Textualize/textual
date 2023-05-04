from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.css.constants import VALID_BORDER
from textual.widgets import Button, Label

TEXT = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain."""


class BorderButtons(Vertical):
    DEFAULT_CSS = """
    BorderButtons {
        dock: left;
        width: 24;
        overflow-y: scroll;
    }

    BorderButtons > Button {
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        for border in sorted(VALID_BORDER):
            if border:
                yield Button(border, id=border)


class BorderApp(App):
    """Demonstrates the border styles."""

    CSS = """
    Screen {
        align: center middle;
        overflow: auto;
    }
    #text {
        margin: 2 4;
        padding: 2 4;
        border: solid $secondary;
        height: auto;
        background: $panel;
        color: $text;
        border-title-align: center;
    }
    """

    def compose(self):
        yield BorderButtons()
        self.text = Label(TEXT, id="text")
        self.text.shrink = True
        self.text.border_title = "solid"
        yield self.text

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.text.border_title = event.button.id
        self.text.styles.border = (
            event.button.id,
            self.stylesheet._variables["secondary"],
        )


app = BorderApp()

if __name__ == "__main__":
    app.run()
