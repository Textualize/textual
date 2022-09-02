from textual.app import App
from textual import layout
from textual.widget import Widget


class FiftyApp(App):

    DEFAULT_CSS = """
    Screen {
        layout: vertical;
    }
    Horizontal {
        height: 50%;
    }
    Widget {
        width: 50%;
        outline: white;
        background: blue;
    }
    
    """

    def compose(self):
        yield layout.Horizontal(Widget(), Widget())
        yield layout.Horizontal(Widget(), Widget())


app = FiftyApp()
if __name__ == "__main__":
    app.run()
