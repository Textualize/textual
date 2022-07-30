from textual.app import App
from textual.widget import Widget


class WidthApp(App):
    CSS = """    
    Screen > Widget {             
        height: 5;
        background: blue;        
        color: white;   
        border: heavy white;     
    }
    Widget.hidden {
        display: none;
    }
    """

    def compose(self):
        yield Widget(id="widget1")
        yield Widget(id="widget2", classes="hidden")
        yield Widget(id="widget3")


app = WidthApp()
