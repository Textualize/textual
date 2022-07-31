from textual.app import App, ComposeResult
from textual.constants import BORDERS
from textual.widgets import Button, Static
from textual import layout


TEXT = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain."""


class BorderButtons(layout.Vertical):
    CSS = """
    BorderButtons {
        dock: left;
        width: 20;
    }

    BorderButtons > Button {
        width: 20;
    }
    """

    def compose(self) -> ComposeResult:
        for border in BORDERS:
            if border:
                yield Button(border, id=border)


class BorderApp(App):
    """Displays a pride flag."""

    COLORS = ["red", "orange", "yellow", "green", "blue", "purple"]

    CSS = """
    Screen {
        background: $surface;
    }
    Static {
        margin: 2 4;
        padding: 2 4;
        border: solid $warning;
        height: auto;
        background: $panel;
        color: $text-panel-fade-1;
    }
    """

    def compose(self):
        self.dark = True
        yield BorderButtons()
        self.text = Static(TEXT)
        yield self.text

    def handle_pressed(self, event):
        self.text.styles.border = (
            event.button.id,
            self.stylesheet.variables["warning"],
        )
        self.bell()


app = BorderApp()

if __name__ == "__main__":
    app.run()
