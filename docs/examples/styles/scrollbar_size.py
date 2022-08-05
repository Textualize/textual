from textual.app import App
from textual import layout
from textual.widgets import Static

TEXT = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain.
"""


class ScrollbarApp(App):
    CSS = """
    Screen {
        background: white;
        color: blue 80%;
        layout: horizontal;
    }
    
    Static {
        padding: 1 2;
        width: 200;
    }

    .panel {
        scrollbar-size: 10 4;
        padding: 1 2;        
    }     
    """

    def compose(self):
        yield layout.Vertical(Static(TEXT * 5), classes="panel")


app = ScrollbarApp()
