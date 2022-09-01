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
        width: 24;
    }

    BorderButtons > Button {
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        for border in BORDERS:
            if border:
                yield Button(border, id=border)


class BorderApp(App):
    """Demonstrates the border styles."""

    CSS = """
    Static {
        margin: 2 4;
        padding: 2 4;
        border: solid $primary;
        height: auto;
        background: $panel;
        color: $text-panel;
    }
    """

    def compose(self):
        yield BorderButtons()
        self.text = Static(TEXT)
        yield self.text

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.text.styles.border = (
            event.button.id,
            self.stylesheet.variables["primary"],
        )
        self.bell()


app = BorderApp()

if __name__ == "__main__":
    app.run()
