from rich.console import RenderableType
from rich.panel import Panel

from textual import events
from textual.app import App
from textual.renderables._tab_headers import Tab
from textual.widget import Widget
from textual.widgets.tabs import Tabs


class PanelWidget(Widget):
    def render(self) -> RenderableType:
        return Panel("hello world!", title="Title")


class BasicApp(App):
    """Sandbox application used for testing/development by Textual developers"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tabs = Tabs(
            [
                Tab("One", name="one"),
                Tab("Two", name="two"),
                Tab("Three", name="three"),
                Tab("Four", name="four"),
                Tab("Five", name="five"),
                Tab("Six", name="six"),
                Tab("SixHundred", name="seven"),
                Tab("Eight", name="eight"),
            ],
            active_tab="three",
            tab_padding=1,
        )
        self.tab_keys = {
            "1": "one",
            "2": "two",
            "3": "three",
            "4": "four",
            "5": "five",
            "6": "six",
            "7": "seven",
            "8": "eight",
        }

    def on_load(self):
        """Bind keys here."""
        self.bind("tab", "toggle_class('#sidebar', '-active')")
        self.bind("a", "toggle_class('#header', '-visible')")
        self.bind("c", "toggle_class('#content', '-content-visible')")
        self.bind("d", "toggle_class('#footer', 'dim')")

    def on_key(self, event: events.Key) -> None:
        self.tabs.active_tab_name = self.tab_keys.get(event.key, "one")

    def on_mount(self):
        """Build layout here."""
        self.mount(
            header=self.tabs,
            content=PanelWidget(),
            footer=Widget(),
            sidebar=Widget(),
        )


BasicApp.run(css_file="dev_sandbox.scss", watch_css=True, log="textual.log")
