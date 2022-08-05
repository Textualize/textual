from textual.app import App
from textual.widgets import Static


class ColorApp(App):
    CSS = """
    Static {
        height:1fr;
        content-align: center middle;
    }    
    #static1 {
        color: red;
    }
    #static2 {
        color: rgb(0, 255, 0);
    }
    #static3 {
        color: hsl(240, 100%, 50%)
    }
    """

    def compose(self):
        yield Static("I'm red!", id="static1")
        yield Static("I'm rgb(0, 255, 0)!", id="static2")
        yield Static("I'm hsl(240, 100%, 50%)!", id="static3")


app = ColorApp()
