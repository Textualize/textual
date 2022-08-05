from textual.app import App
from textual.widgets import Static


class DisplayApp(App):
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
    Static.remove {
        display: none;
    }
    """

    def compose(self):
        yield Static("Widget 1")
        yield Static("Widget 2", classes="remove")
        yield Static("Widget 3")


app = DisplayApp()
