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
        dock:left;
    }
    #two {
        background: blue;
        width:30;
        height: 20;
        dock:left;
    }

    """

    def compose(self) -> ComposeResult:
        yield Static("One", id="one")
        yield Static("Two", id="two")


app = OrderApp()
if __name__ == "__main__":
    app.run()
