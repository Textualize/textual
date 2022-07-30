from textual.app import App
from textual.widgets import Static


class VisibilityApp(App):
    CSS = """    
    Screen {
        background: green;
    }
    Static {             
        height: 5;        
        background: white;        
        color: blue;   
        border: heavy blue;     
    }
    Static.invisible {
        visibility: hidden;
    }
    """

    def compose(self):
        yield Static("Widget 1")
        yield Static("widget 2", classes="invisible")
        yield Static("widget 3")


app = VisibilityApp()
