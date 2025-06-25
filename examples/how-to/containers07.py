from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll
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
        with HorizontalScroll(classes="with-border"):
            for n in range(10):
                yield Box(label=f"Box {n+1}")


if __name__ == "__main__":
    app = ContainerApp()
    app.run()
