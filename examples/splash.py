from time import time

from textual.app import App, ComposeResult, RenderableType
from textual.containers import Container
from textual.renderables.gradient import LinearGradient
from textual.widgets import Static

COLORS = [
    "#881177",
    "#aa3355",
    "#cc6666",
    "#ee9944",
    "#eedd00",
    "#99dd55",
    "#44dd88",
    "#22ccbb",
    "#00bbcc",
    "#0099cc",
    "#3366bb",
    "#663399",
]
STOPS = [(i / (len(COLORS) - 1), color) for i, color in enumerate(COLORS)]


class Splash(Container):
    """Custom widget that extends Container."""

    DEFAULT_CSS = """
    Splash {
        align: center middle;
    }
    Static {
        width: 40;
        padding: 2 4;
    }
    """

    def on_mount(self) -> None:
        self.auto_refresh = 1 / 30

    def compose(self) -> ComposeResult:
        yield Static("Making a splash with Textual!")

    def render(self) -> RenderableType:
        return LinearGradient(time() * 90, STOPS)


class SplashApp(App):
    """Simple app to show our custom widget."""

    def compose(self) -> ComposeResult:
        yield Splash()


if __name__ == "__main__":
    app = SplashApp()
    app.run()
    print("https://textual.textualize.io/how-to/render-and-compose/")
