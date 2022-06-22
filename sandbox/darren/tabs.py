from dataclasses import dataclass

from rich.console import RenderableType
from rich.padding import Padding
from rich.rule import Rule
from rich.style import Style

from textual import events
from textual.app import App
from textual.widget import Widget
from textual.widgets.tabs import Tabs, Tab


class Hr(Widget):
    def render(self) -> RenderableType:
        return Rule()


class Info(Widget):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.text = text

    def render(self) -> RenderableType:
        return Padding(f"{self.text}", pad=(0, 1))


@dataclass
class WidgetDescription:
    description: str
    widget: Widget


class BasicApp(App):
    """Sandbox application used for testing/development by Textual developers"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keys_to_tabs = {
            "1": Tab("January", name="one"),
            "2": Tab("に月", name="two"),
            "3": Tab("March", name="three"),
            "4": Tab("April", name="four"),
            "5": Tab("May", name="five"),
            "6": Tab("And a really long tab!", name="six"),
        }
        tabs = list(self.keys_to_tabs.values())
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
            WidgetDescription(
                "Change the styling of active and inactive labels (active_tab_style, inactive_tab_style)",
                Tabs(
                    tabs,
                    active_tab="one",
                    active_bar_style="#DA812D",
                    active_tab_style="bold #FFCB4D on #021720",
                    inactive_tab_style="italic #887AEF on #021720",
                    inactive_bar_style="#695CC8",
                    inactive_text_opacity=0.6,
                ),
            ),
            WidgetDescription(
                "Change the animation duration and function (animation_duration=1, animation_function='out_quad')",
                Tabs(
                    tabs,
                    active_tab="one",
                    active_bar_style="#887AEF",
                    inactive_text_opacity=0.2,
                    animation_duration=1,
                    animation_function="out_quad",
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
        ]

    def on_load(self):
        """Bind keys here."""
        self.bind("tab", "toggle_class('#sidebar', '-active')")
        self.bind("a", "toggle_class('#header', '-visible')")
        self.bind("c", "toggle_class('#content', '-content-visible')")
        self.bind("d", "toggle_class('#footer', 'dim')")

    def on_key(self, event: events.Key) -> None:
        for example in self.examples:
            tab = self.keys_to_tabs.get(event.key)
            if tab:
                example.widget._active_tab_name = tab.name

    def on_mount(self):
        """Build layout here."""
        self.mount(
            info=Info(
                "\n"
                "• The examples below show customisation options for the [bold #1493FF]Tabs[/] widget.\n"
                "• Press keys 1-6 on your keyboard to switch tabs, or click on a tab.",
            )
        )
        for example in self.examples:
            info = Info(example.description)
            self.mount(Hr())
            self.mount(info)
            self.mount(example.widget)


app = BasicApp(css_path="tabs.scss", watch_css=True, log_path="textual.log")
app.run()
