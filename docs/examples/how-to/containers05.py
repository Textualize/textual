from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup
from textual.widgets import Placeholder


class Box(Placeholder):
    """Example widget."""

    DEFAULT_CSS = """
    Box {
        width: 16;
        height: 8;        
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
        with HorizontalGroup(classes="with-border"):
            yield Box()
            yield Box()
            yield Box()
        with HorizontalGroup(classes="with-border"):
            yield Box()
            yield Box()
            yield Box()


if __name__ == "__main__":
    app = ContainerApp()
    app.run()
