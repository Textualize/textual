from textual.app import App
from textual.widgets import Static


class BoxSizingApp(App):
    CSS = """
    Screen {
        background: white;
        color: black;
    }
    Static {
        background: blue 20%;
        height: 5;
        margin: 2;
        padding: 1;
        border: wide black;
    }
    #static1 {       
        box-sizing: border-box;
    }
    #static2 {        
        box-sizing: content-box;
    }

    """

    def compose(self):
        yield Static("I'm using border-box!", id="static1")
        yield Static("I'm using content-box!", id="static2")


app = BoxSizingApp()
