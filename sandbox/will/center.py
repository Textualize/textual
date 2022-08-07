from textual.app import App
from textual.widgets import Static


class CenterApp(App):
    CSS = """
    
    Screen {
        layout: center;
        overflow: auto auto;
    }

    Static {
        border: wide $primary;
        background: $panel;
        width: 50;
        height: 20;
        margin: 1 2;
        content-align: center middle;
    }
    
    """

    def compose(self):
        yield Static("Hello World!")


app = CenterApp()
