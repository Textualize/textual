from __future__ import annotations

from rich.style import Style
from rich.text import TextType

from .. import events
from ..app import ComposeResult, RenderResult
from ..containers import Horizontal, Vertical
from ..css.query import NoMatches
from ..geometry import Offset
from ..message import Message
from ..reactive import reactive
from ..renderables.underline_bar import UnderlineBar
from ..widget import Widget
from ..widgets import Static


class Underline(Widget):
    DEFAULT_CSS = """
    Underline {
        width: 100%;
        height: 1;

    }

    Underline > .underline--bar {
        background: $foreground 10%;
        color: $accent;
    }

    """

    COMPONENT_CLASSES = {"underline--bar"}

    highlight_start = reactive(0)
    highlight_end = reactive(0)

    class Clicked(Message):
        def __init__(self, offset: Offset) -> None:
            self.offset = offset
            super().__init__()

    @property
    def _highlight_range(self) -> tuple[int, int]:
        """Highlighted range for underline bar."""
        return (self.highlight_start, self.highlight_end)

    def render(self) -> RenderResult:
        bar_style = self.get_component_rich_style("underline--bar")

        return UnderlineBar(
            highlight_range=self._highlight_range,
            highlight_style=Style.from_color(bar_style.color),
            background_style=Style.from_color(bar_style.bgcolor),
        )

    def on_click(self, event: events.Click):
        self.post_message(self.Clicked(event.offset))


class Tab(Static):
    DEFAULT_CSS = """
    Tab {
        width: auto;
        height: 2;
        padding: 1 2 0 2;
        text-align: center;
        color: $text-muted;
    }

    Tab.-selected {
        text-style: bold;
        color: $text;
    }

    Tab:hover {


    }

    """

    class Clicked(Message):
        def __init__(self, tab: Tab) -> None:
            self.tab = tab
            super().__init__()

    def __init__(
        self,
        label: TextType,
        content_id: str,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.content_id = content_id
        self.label = label
        self.update(label)

    def on_click(self):
        self.post_message(self.Clicked(self))


class Tabs(Widget):
    DEFAULT_CSS = """
    Tabs {
        width: 100%;
        height: 3;

    }
    Tabs Horizontal {

    }
    """

    highlighted: reactive[str] = reactive(str)
    selected: reactive[str] = reactive(str)

    def __init__(
        self,
        *tabs: Tab,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.tabs = tabs

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield from self.tabs
            yield Underline()

    def watch_selected(self, selected: str) -> None:
        if not selected:
            return
        self.highlight_selected()

    def highlight_selected(self, animate: bool = True) -> None:
        underline = self.query_one(Underline)
        try:
            selected_tab = self.query_one(f"Tab.-selected")
        except NoMatches:
            underline.highlight_start = 0
            underline.highlight_end = 0
        else:
            tab_region = selected_tab.virtual_region.shrink(selected_tab.styles.gutter)
            start, end = tab_region.column_span
            if animate:
                underline.animate("highlight_start", start, duration=0.3)
                underline.animate("highlight_end", end, duration=0.3)
            else:
                underline.highlight_start = start
                underline.highlight_end = end

    def on_tab_clicked(self, event: Tab.Clicked) -> None:
        event.stop()
        self.query("Tab.-selected").remove_class("-selected")
        event.tab.add_class("-selected")
        self.selected = event.tab.content_id

    def on_underline_clicked(self, event: Underline.Clicked) -> None:
        event.stop()

    def on_resize(self):
        self.highlight_selected(animate=False)


if __name__ == "__main__":
    from textual.app import App

    class TabsApp(App):
        def compose(self) -> ComposeResult:
            yield Tabs(
                Tab("Foo", "foo"),
                Tab("bar", "bar"),
                Tab("A much longer tab header", "long_tab"),
                Tab("Paul", "paul"),
                Tab("Jessica", "jessica"),
            )

    app = TabsApp()
    app.run()
