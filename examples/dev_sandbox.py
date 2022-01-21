from rich.console import RenderableType
from rich.panel import Panel

from textual.app import App
from textual.widget import Widget


class PanelWidget(Widget):
    def render(self) -> RenderableType:
        return Panel("hello world!", title="Title")


class BasicApp(App):
    """Sandbox application used for testing/development by Textual developers"""

    def on_load(self):
        """Bind keys here."""
        self.bind("tab", "toggle_class('#sidebar', '-active')")
        self.bind("a", "toggle_class('#header', '-visible')")
        self.bind("c", "toggle_class('#content', '-content-visible')")

    def on_mount(self):
        """Build layout here."""
        self.mount(
            header=Widget(),
            content=PanelWidget(),
            footer=Widget(),
            sidebar=Widget(),
        )


BasicApp.run(css_file="test_app.css", watch_css=True, log="textual.log")
