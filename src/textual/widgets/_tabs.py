from __future__ import annotations

from rich.style import Style
from rich.text import Text, TextType

from .. import events
from ..app import ComposeResult, RenderResult
from ..binding import Binding
from ..containers import Container, Horizontal, Vertical
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
        width: 1fr;
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
        self.post_message(self.Clicked(event.screen_offset))


class Tab(Static):
    DEFAULT_CSS = """
    Tab {
        width: auto;

        height: 2;
        padding: 1 2 0 2;
        text-align: center;
        color: $text-disabled;
    }

    Tab.-active {
        text-style: bold;
        color: $text;
    }
    Tab:hover {

        text-style: bold;
    }
    Tab.-active:hover {
        color: $text;

    }


    """

    class Clicked(Message):
        def __init__(self, tab: Tab) -> None:
            self.tab = tab
            super().__init__()

    def __init__(
        self,
        label: TextType,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        if id is None:
            label_text = str(label)
            id = f"tab-{label_text.replace(' ', '-')}"
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.label = label
        self.update(label)

    def on_click(self):
        self.post_message(self.Clicked(self))


class Tabs(Widget, can_focus=True):
    DEFAULT_CSS = """
    Tabs {
        width: 100%;
        height:3;
    }

    Tabs > #tabs-scroll {
        overflow: hidden;
    }

    Tabs #tabs-list {
       width: auto;

    }

    Tabs #tabs-list-bar, Tabs #tabs-list {
        width: auto;
        height: auto;
        min-width: 100%;
        overflow: hidden hidden;
    }
    Tabs:focus .underline--bar {

        background: $foreground 20%;
    }
    """

    BINDINGS = [
        Binding("left", "previous_tab", "Previous tab", show=False),
        Binding("right", "next_tab", "Next tab", show=False),
    ]

    highlighted: reactive[str] = reactive(str)
    active: reactive[str] = reactive(str)

    def __init__(
        self,
        *tabs: Tab | TextType,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        add_tabs = [(Tab(tab) if isinstance(tab, (str, Text)) else tab) for tab in tabs]
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.tabs = add_tabs

    @property
    def active_tab(self) -> Tab:
        return self.query_one("Tab.-active", Tab)

    def on_mount(self) -> None:
        tab = self.query(Tab).first(Tab)
        self.active = tab.id or ""

    def compose(self) -> ComposeResult:
        with Container(id="tabs-scroll"):
            with Vertical(id="tabs-list-bar"):
                with Horizontal(id="tabs-list"):
                    yield from self.tabs
                yield Underline()

    def watch_active(self, previously_active: str, active: str) -> None:
        if active:
            active_tab = self.query_one(f"#{active}")
            self.query("Tab.-active").remove_class("-active")
            active_tab.add_class("-active")
            self._highlight_active(animate=previously_active != "")

    def _highlight_active(self, animate: bool = True) -> None:
        underline = self.query_one(Underline)
        try:
            active_tab = self.query_one(f"Tab.-active")
        except NoMatches:
            underline.highlight_start = 0
            underline.highlight_end = 0
        else:
            tab_region = active_tab.virtual_region.shrink(active_tab.styles.gutter)
            start, end = tab_region.column_span
            if animate:
                underline.animate("highlight_start", start, duration=0.3)
                underline.animate("highlight_end", end, duration=0.3)
            else:
                underline.highlight_start = start
                underline.highlight_end = end

    def on_tab_clicked(self, event: Tab.Clicked) -> None:
        self.focus()
        event.stop()
        self._activate_tab(event.tab)

    def _activate_tab(self, tab: Tab) -> None:
        self.query("Tab.-active").remove_class("-active")
        tab.add_class("-active")
        self.active = tab.id or ""
        self.query_one("#tabs-scroll").scroll_to_widget(tab, force=True)

    def on_underline_clicked(self, event: Underline.Clicked) -> None:
        event.stop()
        offset = event.offset + (0, -1)
        for tab in self.query(Tab):
            if offset in tab.region:
                self._activate_tab(tab)
                break

    def on_resize(self):
        self._highlight_active(animate=False)
        self.query_one("#tabs-scroll").scroll_to_widget(self.active_tab, force=True)

    def action_next_tab(self) -> None:
        active_tab = self.active_tab
        tabs = list(self.query(Tab))
        tab_count = len(tabs)
        new_tab_index = (tabs.index(active_tab) + 1) % tab_count
        self.active = tabs[new_tab_index].id or ""
        self.query_one("#tabs-scroll").scroll_to_widget(self.active_tab, force=True)

    def action_previous_tab(self) -> None:
        active_tab = self.active_tab
        tabs = list(self.query(Tab))
        tab_count = len(tabs)
        new_tab_index = (tabs.index(active_tab) - 1) % tab_count
        self.active = tabs[new_tab_index].id or ""
        self.query_one("#tabs-scroll").scroll_to_widget(self.active_tab, force=True)


if __name__ == "__main__":
    from textual.app import App

    class TabsApp(App):
        def compose(self) -> ComposeResult:
            yield Tabs(
                Tab("Foo"),
                Tab("bar"),
                Tab("A much longer tab header"),
                Tab("Paul"),
                Tab("Jessica"),
                Tab("Duncan"),
                Tab("Chani"),
            )

            yield Tabs("a", "b")

            yield Tabs("One", "Two", "Three")

    app = TabsApp()
    app.run()
