from textual.app import App
from textual.widgets import Static


class BorderApp(App):
    CSS = """
    Screen {
        background: white;
    }
    Screen > Static {
        height:5;
        content-align: center middle;
        color: white;
        margin: 1;
        box-sizing: border-box;
    }    
    #static1 {
        background: red 20%;
        color: red;
        border: solid red;
    }
    #static2 {
        background: green 20%;
        color: green;
        border: dashed green;

    }
    #static3 {
        background: blue 20%;
        color: blue;
        border: tall blue;
    }
    """

    def compose(self):
        yield Static("Hello, World!", id="static1")
        yield Static("Hello, World!", id="static2")
        yield Static("Hello, World!", id="static3")


app = BorderApp()
