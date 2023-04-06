from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import Label


class FRApp(App):
    CSS = """    
    Screen {
        align: center middle;
        border: solid cyan;
    }

    #container {  
        width: 30;      
        height: auto;
        border: solid green;
        overflow-y: auto;
    }

    #child {
        height: 1fr;
        border: solid red;       
    }

    #bottom {
        margin: 1 2;    
        background: $primary;
    }
    """

    def compose(self) -> ComposeResult:
        with Widget(id="container"):
            yield Label("Hello one line", id="top")
            yield Widget(id="child")
            yield Label("Two\nLines with 1x2 margin", id="bottom")


if __name__ == "__main__":
    app = FRApp()
    app.run()
