from textual.app import App
from textual.widget import Widget


class WidthApp(App):
    CSS = """    
    Widget {     
        background: blue 50%;
        width: 50%;
    }
    """

    def compose(self):
        yield Widget()


app = WidthApp()
