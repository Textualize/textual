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
        yield Static("Widget 2", classes="invisible")
        yield Static("Widget 3")


app = VisibilityApp()
