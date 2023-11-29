from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.containers import Horizontal, Vertical, Grid


class Box(Static):
    pass


class KeylineApp(App):
    CSS = """
    Vertical {
        keyline: thin red;
    }
    Horizontal {
        keyline: heavy green;
    }
    Grid {
        keyline: double magenta;
    }
    Box {
        width: 1fr;
        height: 1fr;        
    }
    Horizontal > Box, Vertical > Box {
        margin: 1;
    }
    Grid {
        grid-size: 2;
        grid-gutter: 1;
    }

    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Box("1")
            yield Box("2")
            yield Box("3")
        with Horizontal():
            yield Box("4")
            yield Box("5")
            yield Box("6")
        with Grid():
            yield Box("7")
            yield Box("8")
            yield Box("9")


if __name__ == "__main__":
    app = KeylineApp()
    app.run()
