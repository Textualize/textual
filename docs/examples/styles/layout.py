from textual import layout
from textual.app import App
from textual.widget import Widget
from textual.widgets import Static


class LayoutApp(App):
    CSS = """
    #vertical-layout {
        layout: vertical;
        background: $panel;
        height: auto;
    }
    #horizontal-layout {
        layout: horizontal;
        background: $panel-darken-1;
        height: auto;
    }
    #center-layout {
        layout: center;
        background: $panel-darken-2;
        height: 7;
    }
    Screen Static {
        margin: 1;
        width: 12;
        color: $text-primary;
        background: $primary;
    }
    """

    def compose(self):
        yield layout.Container(
            Static("Layout"),
            Static("Is"),
            Static("Vertical"),
            id="vertical-layout",
        )
        yield layout.Container(
            Static("Layout"),
            Static("Is"),
            Static("Horizontal"),
            id="horizontal-layout",
        )
        yield layout.Container(
            Static("Center"),
            id="center-layout",
        )


app = LayoutApp()
app.run()
