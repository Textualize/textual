from rich.console import RenderableType
from rich.panel import Panel

from textual.app import App
from textual.widget import Widget


class PanelWidget(Widget):
    def render(self) -> RenderableType:
        return Panel("hello world!", title="Title", height=4)


class BasicApp(App):
    """Sandbox application used for testing/development by Textual developers"""

    def on_load(self):
        """Bind keys here."""
        self.bind("tab", "toggle_class('#sidebar', '-active')")
        self.bind("a", "toggle_class('#header', '-visible')")
        self.bind("c", "toggle_class('#content', '-content-visible')")

    def on_mount(self):
        """Build layout here."""
        self.mount(header=PanelWidget(), content=PanelWidget(), footer=PanelWidget())
        self.view.refresh_layout()


BasicApp.run(log="textual.log")
