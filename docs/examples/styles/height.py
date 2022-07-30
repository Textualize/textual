from textual.app import App
from textual.widget import Widget


class WidthApp(App):
    CSS = """    
    Screen > Widget {     
        background: green;
        height: 50%;
        color: white;
    }
    """

    def compose(self):
        yield Widget()


app = WidthApp()
