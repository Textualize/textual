from textual.app import App, ComposeResult
from textual.widgets import Static


class OrderApp(App):

    CSS = """
    Screen {
        layout: center;
    }
    Static {
        border: heavy white;
    }
    #one {
        background: red;
        width:20;
        height: 30;
    }
    #two {
        background: blue;
        width:30;
        height: 20;
    }
    #three {
        background: green;
        width:40;
        height:10
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("One", id="one")
        yield Static("Two", id="two")
        yield Static("Three", id="three")


app = OrderApp()
if __name__ == "__main__":
    app.run()
