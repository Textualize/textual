from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, Middle
from textual.widgets import Placeholder


class Box(Placeholder):
    """Example widget."""

    DEFAULT_CSS = """
    Box {
        width: 16;
        height: 5;        
    }
    """


class ContainerApp(App):
    """Simple app to play with containers."""

    CSS = """
    .with-border {
        border: heavy green;
    }
    """

    def compose(self) -> ComposeResult:
        with HorizontalGroup():
            yield Box("Box 1")
            with Middle(classes="with-border"):
                yield Box("Box 2")
            yield Box("Box 3")


if __name__ == "__main__":
    app = ContainerApp()
    app.run()
