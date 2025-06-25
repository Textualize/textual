from textual.app import App, ComposeResult
from textual.containers import Center, Right
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
        yield Box("Box 1")  # (1)!
        with Center(classes="with-border"):  # (2)!
            yield Box("Box 2")
        with Right(classes="with-border"):  # (3)!
            yield Box("Box 3")


if __name__ == "__main__":
    app = ContainerApp()
    app.run()
