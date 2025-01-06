from textual.app import App, ComposeResult

from textual.widgets import Label

from textual.containers import VerticalGroup
from textual.content import Content

TEXT = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain."""


class MyApp(App):
    CSS = """
    VerticalGroup {
        layout: grid;
        grid-size: 3 3;
        grid-columns: 1fr;
        grid-rows: auto;
        height: auto;      
    }
    Label {
        padding: 2 4;        
        border: heavy red;

	    &.left {
            text-align: left;
        }
        &.center {
            text-align: center;
        }
        &.right {
            text-align: right;
        }       
         &.justify {
            text-align: justify;
        }   
    }
    """

    def compose(self) -> ComposeResult:
        with VerticalGroup():
            yield Label(TEXT, classes="left", id="first")
            yield Label(TEXT, classes="left")
            yield Label(TEXT, classes="center")
            yield Label(TEXT, classes="center")
            yield Label(TEXT, classes="right")
            yield Label(TEXT, classes="right")
            yield Label(TEXT, classes="justify")
            yield Label(TEXT, classes="justify")
            yield Label(TEXT, classes="justify", id="last")


if __name__ == "__main__":
    MyApp().run()
