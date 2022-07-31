from textual.app import App
from textual.widgets import Static


class OffsetApp(App):
    CSS = """  
    Screen {
        background: white;
        color: black;
        layout: horizontal;
    }
    Static {             
        width: 20;
        height: 10;
        content-align: center middle; 
    }

    .paul {
        offset: 8 2;
        background: red 20%;
        border: outer red;
        color: red;
    }

    .duncan {
        offset: 4 10;
        background: green 20%;
        border: outer green;
        color: green;
    }

    .chani {
        offset: 0 5;
        background: blue 20%;
        border: outer blue;
        color: blue;
    }
    """

    def compose(self):
        yield Static("Paul", classes="paul")
        yield Static("Duncan", classes="duncan")
        yield Static("Chani", classes="chani")


app = OffsetApp()
