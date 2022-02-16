from dataclasses import dataclass

from rich.console import RenderableType
from rich.padding import Padding

from textual import events
from textual.app import App
from textual.renderables._tab_headers import Tab
from textual.widget import Widget
from textual.widgets.tabs import Tabs


class Info(Widget):
    def __init__(self, text: str, emoji: bool = True) -> None:
        super().__init__()
        self.text = text
        self.emoji = emoji

    def render(self) -> RenderableType:
        prefix = "ℹ️  " if self.emoji else ""
        return Padding(f"{prefix}{self.text}", pad=1)


@dataclass
class WidgetDescription:
    description: str
    widget: Widget


class BasicApp(App):
    """Sandbox application used for testing/development by Textual developers"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tab_keys = {
            "1": "one",
            "2": "two",
            "3": "three",
            "4": "four",
            "5": "five",
            "6": "six",
        }
        tabs = [
            Tab("January", name="one"),
            Tab("に月", name="two"),
            Tab("March", name="three"),
            Tab("April", name="four"),
            Tab("May", name="five"),
            Tab("And a really long tab!", name="six"),
            # Tab("Four", name="five"),
            # Tab("Four", name="six"),
            # Tab("Four", name="seven"),
            # Tab("Four", name="eight"),
            # Tab("Four", name="nine"),
        ]
        self.examples = [
            WidgetDescription(
                "Customise the spacing between tabs, e.g. tab_padding=1",
                Tabs(
                    tabs,
                    tab_padding=1,
                ),
            ),
            WidgetDescription(
                "Change the opacity of inactive tab text, e.g. inactive_text_opacity=.2",
                Tabs(
                    tabs,
                    active_tab="two",
                    active_bar_style="#1493FF",
                    inactive_text_opacity=0.2,
                    tab_padding=2,
                ),
            ),
            WidgetDescription(
                "Choose which tab to start on by name, e.g. active_tab='three'",
                Tabs(
                    tabs,
                    active_tab="three",
                    active_bar_style="#FFCB4D",
                    tab_padding=3,
                ),
            ),
            WidgetDescription(
                "Change the color of the inactive portions of the underline, e.g. inactive_bar_style='blue'",
                Tabs(
                    tabs,
                    active_tab="four",
                    inactive_bar_style="blue",
                ),
            ),
            WidgetDescription(
                "Change the color of the active portion of the underline, e.g. active_bar_style='red'",
                Tabs(
                    tabs,
                    active_tab="five",
                    active_bar_style="red",
                    inactive_text_opacity=1,
                ),
            ),
        ]

    def on_load(self):
        """Bind keys here."""
        self.bind("tab", "toggle_class('#sidebar', '-active')")
        self.bind("a", "toggle_class('#header', '-visible')")
        self.bind("c", "toggle_class('#content', '-content-visible')")
        self.bind("d", "toggle_class('#footer', 'dim')")

    def on_key(self, event: events.Key) -> None:
        for example in self.examples:
            example.widget.active_tab_name = self.tab_keys.get(event.key, "one")

    def on_mount(self):
        """Build layout here."""
        self.mount(
            info=Info(
                "• The examples below show customisation options for the [#1493FF]Tabs[/] widget.\n"
                "• Press keys 1-6 on your keyboard to switch tabs, or click on a tab.",
                emoji=False,
            )
        )
        for example in self.examples:
            self.mount(Info(example.description))
            self.mount(example.widget)


BasicApp.run(css_file="tabs.scss", watch_css=True, log="textual.log")
