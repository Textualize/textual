from textual.app import App
from textual.widgets import Static


class BackgroundApp(App):
    CSS = """
    Static {
        height: 1fr;
        content-align: center middle;
        color: white;
    }    
    #static1 {
        background: red;
    }
    #static2 {
        background: rgb(0, 255, 0);
    }
    #static3 {
        background: hsl(240, 100%, 50%);
    }
    """

    def compose(self):
        yield Static("Widget 1", id="static1")
        yield Static("Widget 2", id="static2")
        yield Static("Widget 3", id="static3")


app = BackgroundApp()
