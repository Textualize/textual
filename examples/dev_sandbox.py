from rich.console import RenderableType
from rich.panel import Panel

from textual.app import App
from textual.renderables._tab_headers import Tab
from textual.widget import Widget
from textual.widgets.tabs import Tabs


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

    def on_mount(self):
        """Build layout here."""
        self.mount(
            header=Tabs(
                [
                    Tab("One", active=True),
                    Tab("Two"),
                    Tab("Three"),
                    Tab("Four"),
                    Tab("Five"),
                    Tab("Six"),
                ]
            ),
            content=PanelWidget(),
            footer=Widget(),
            sidebar=Widget(),
        )


BasicApp.run(css_file="dev_sandbox.scss", watch_css=True, log="textual.log")
