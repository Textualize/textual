from textual.app import App
from textual.widgets import Static


class ContentAlignApp(App):
    CSS = """
    #box1 {
        content-align: left top;
        background: $panel;
    }
    #box2 {
        content-align: center middle;
        background: $panel-darken-1;
    }
    #box3 {
        content-align: right bottom;
        background: $panel-darken-2;
    }
    ContentAlignApp Static {
        padding: 1;
        height: 1fr;
    }
    """

    def compose(self):
        yield Static("With [i]content-align[/] you can...", id="box1")
        yield Static("...[b]Easily align content[/]...", id="box2")
        yield Static("...Horizontally [i]and[/] vertically!", id="box3")


app = ContentAlignApp()
