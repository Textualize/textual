from textual.app import App, ComposeResult
from textual.containers import Middle
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
        with Middle(classes="with-border"):  # (1)!
            yield Box("Box 1.")
            yield Box("Box 2.")
            yield Box("Box 3.")


if __name__ == "__main__":
    app = ContainerApp()
    app.run()
