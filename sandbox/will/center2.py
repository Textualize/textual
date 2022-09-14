from textual.app import App
from textual.layout import Vertical, Center
from textual.widgets import Static


class CenterApp(App):
    DEFAULT_CSS = """

    #sidebar {
        dock: left;
        width: 32;
        height: 100%;
        border-right: vkey $primary;
    }

    #bottombar {
        dock: bottom;
        height: 12;
        width: 100%;
        border-top: hkey $primary;
    }

    #hello {
        border: wide $primary;
        width: 40;
        height: 16;      
        margin: 2 4;  
    }

    #sidebar.hidden {
       width: 0;
    }

    Static {        
        background: $panel;
        color: $text;
        content-align: center middle;
    }
    
    """

    def on_mount(self) -> None:
        self.bind("t", "toggle_class('#sidebar', 'hidden')")

    def compose(self):
        yield Static("Sidebar", id="sidebar")
        yield Vertical(
            Static("Bottom bar", id="bottombar"),
            Center(
                Static("Hello World!", id="hello"),
            ),
        )


app = CenterApp()
