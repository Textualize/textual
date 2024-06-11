from textual.app import App, ComposeResult
from textual.widgets import Label
from textual.containers import Container


class HatchApp(App):
    CSS = """
    Screen {
        hatch: right slateblue;
    }
    #one {
        hatch: left $success;
        margin: 2 4;
    }

    #two {
        hatch: cross $warning;
        margin: 2 4;
    }

    #three {
        hatch: horizontal $error;
        margin: 2 4;
    }

    #four {
        hatch: vertical $primary;
        margin: 1 2;
        padding: 1 2;
        align: center middle;
        border: solid red;
    }

    #five {
        hatch: "┼"  $success 50%;
        margin: 1 2;
        align: center middle;
        text-style: bold;
        color: magenta;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="one"):
            with Container(id="two"):
                with Container(id="three"):
                    with Container(id="four"):
                        with Container(id="five"):
                            yield Label("Hatched")

    def on_mount(self) -> None:
        self.query_one("#four").border_title = "Hello World"


if __name__ == "__main__":
    HatchApp().run()
