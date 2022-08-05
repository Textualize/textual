from textual.app import App
from textual.widgets import Static
from textual.layout import Horizontal, Vertical

TEXT = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain."""


class OverflowApp(App):
    CSS = """
    Screen {
        background: $background;
        color: black;
    }
   
    Vertical {
        width: 1fr;
    }

    Static {
        margin: 1 2;  
        background: blue 20%;  
        border: blue wide;
        height: auto;
    }    

    #right {
        overflow-y: hidden;
    }
    """

    def compose(self):
        yield Horizontal(
            Vertical(Static(TEXT), Static(TEXT), Static(TEXT), id="left"),
            Vertical(Static(TEXT), Static(TEXT), Static(TEXT), id="right"),
        )


app = OverflowApp()
