from textual.app import App
from textual.widgets import Static

TEXT = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain."""


class TextStyleApp(App):
    CSS = """
    Screen {
        layout: horizontal;    
    }
    Static {
        width:1fr;        
    }    
    #static1 {
        background: red 30%;
        text-style: bold;
    }
    #static2 {
        background: green 30%;
        text-style: italic;
    }
    #static3 {
        background: blue 30%;
        text-style: reverse;
    }
    """

    def compose(self):
        yield Static(TEXT, id="static1")
        yield Static(TEXT, id="static2")
        yield Static(TEXT, id="static3")


app = TextStyleApp()
