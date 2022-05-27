from rich.console import RenderableType
from rich.panel import Panel
from rich.style import Style

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
        self.bind("d", "toggle_class('#footer', 'dim')")
        self.bind("x", "dump")

    def on_mount(self):
        """Build layout here."""
        self.mount(
            header=Widget(),
            content=PanelWidget(),
            footer=Widget(),
            sidebar=Widget(),
        )

    def action_dump(self):
        self.panic(self.tree)


BasicApp.run(css_path="dev_sandbox.scss", watch_css=True, log_path="textual.log")
