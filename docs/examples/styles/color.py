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
        yield Static("Hello, World!", id="static1")
        yield Static("Hello, World!", id="static2")
        yield Static("Hello, World!", id="static3")


app = ColorApp()
