from __future__ import annotations

from typing import ClassVar

import rich.repr
from rich.style import Style
from rich.text import Text, TextType

from .. import events
from ..app import ComposeResult, RenderResult
from ..binding import Binding, BindingType
from ..containers import Container, Horizontal, Vertical
from ..css.query import NoMatches
from ..geometry import Offset
from ..message import Message
from ..reactive import reactive
from ..renderables.underline_bar import UnderlineBar
from ..widget import Widget
from ..widgets import Static


class Underline(Widget):
    """The animated underline beneath tabs."""

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
    """A Widget to manage a single tab within a Tabs widget."""

    DEFAULT_CSS = """
    Tab {
        width: auto;
        height: 2;
        padding: 1 1 0 2;
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
        """A tab was clicked."""

        def __init__(self, tab: Tab) -> None:
            self.tab = tab
            super().__init__()

    def __init__(
        self,
        label: TextType,
        *,
        id: str | None = None,
    ) -> None:
        """Initialise a Tab.

        Args:
            label: The label to use in the tab. May be a str or a Text object.
            id: Optional ID for the widget.

        """
        self.label = Text.from_markup(label) if isinstance(label, str) else label
        if id is None:
            id = f"tab-{self.label_text.lower().replace(' ', '-')}"
        super().__init__(id=id)
        self.update(label)

    @property
    def label_text(self) -> str:
        """Undecorated text of the label."""
        return self.label.plain

    def _on_click(self):
        """Inform the message that the tab was clicked."""
        self.post_message(self.Clicked(self))


class Tabs(Widget, can_focus=True):
    """A row of tabs."""

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
       min-height: 2;
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

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("left", "previous_tab", "Previous tab", show=False),
        Binding("right", "next_tab", "Next tab", show=False),
    ]

    class TabActivated(Message):
        """Sent when a new tab is activated."""

        def __init__(self, tab: Tab) -> None:
            self.tab = tab
            super().__init__()

        def __rich_repr__(self) -> rich.repr.Result:
            yield self.tab

    active: reactive[str] = reactive(str, init=False)

    def __init__(
        self,
        *tabs: Tab | TextType,
        active: str | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        """Construct a Tabs widget.

        Args:
            *tabs: Positional argument should be explicit Tab objects, or a str or Text.
            active (_type_, optional): ID of the tab which should be active on start.
            name: Optional name for the input widget.
            id: Optional ID for the widget.
            classes: Optional initial classes for the widget.
            disabled: Whether the input is disabled or not.
        """
        add_tabs = [(Tab(tab) if isinstance(tab, (str, Text)) else tab) for tab in tabs]
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self._tabs = add_tabs
        self._first_active = active

    def add_tab(self, tab: Tab | str | Text) -> None:
        """Add a new tab to the end of the tab list.

        Args:
            tab: A new tab object, or a label (str or Text).
        """
        tab_widget = Tab(tab) if isinstance(tab, (str, Text)) else tab
        self.query_one("#tabs-list").mount(tab_widget)

    def clear(self) -> None:
        self.query_one("#tabs-list > Tab").remove()
        self.active = ""

    def validate_active(self, active: str) -> str:
        """Check id assigned to active attribute is a valid tab."""
        if active and not self.query(f"#tabs-list > #{active}"):
            raise ValueError(f"No Tab with id {active!r}")
        return active

    @property
    def active_tab(self) -> Tab:
        """The currently active tab."""
        return self.query_one("#tabs-list Tab.-active", Tab)

    def on_mount(self) -> None:
        """Make the first tab active."""
        if self._first_active is not None:
            self.active = self._first_active
        if not self.active:
            try:
                tab = self.query("#tabs-list > Tab").first(Tab)
            except NoMatches:
                # Tabs are empty!
                return
            self.active = tab.id or ""

    def compose(self) -> ComposeResult:
        with Container(id="tabs-scroll"):
            with Vertical(id="tabs-list-bar"):
                with Horizontal(id="tabs-list"):
                    yield from self._tabs
                yield Underline()

    def watch_active(self, previously_active: str, active: str) -> None:
        if active:
            active_tab = self.query_one(f"#tabs-list > #{active}", Tab)
            self.query("#tabs-list > Tab.-active").remove_class("-active")
            active_tab.add_class("-active")
            self._highlight_active(animate=previously_active != "")
            print(self.TabActivated(active_tab).handler_name)
            self.post_message(self.TabActivated(active_tab))

    def _highlight_active(self, animate: bool = True) -> None:
        """Move the underline bar to under the active tab,

        Args:
            animate: Should the bar animate?
        """
        underline = self.query_one(Underline)
        try:
            active_tab = self.query_one(f"#tabs-list > Tab.-active")
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

    async def _on_tab_clicked(self, event: Tab.Clicked) -> None:
        self.focus()
        event.stop()
        self._activate_tab(event.tab)

    def _activate_tab(self, tab: Tab) -> None:
        self.query("#tabs-list Tab.-active").remove_class("-active")
        tab.add_class("-active")
        self.active = tab.id or ""
        self.query_one("#tabs-scroll").scroll_to_widget(tab, force=True)

    def _on_underline_clicked(self, event: Underline.Clicked) -> None:
        event.stop()
        offset = event.offset + (0, -1)
        for tab in self.query(Tab):
            if offset in tab.region:
                self._activate_tab(tab)
                break

    def _scroll_active_tab(self) -> None:
        try:
            self.query_one("#tabs-scroll").scroll_to_widget(self.active_tab, force=True)
        except NoMatches:
            pass

    def _on_resize(self):
        self._highlight_active(animate=False)
        self._scroll_active_tab()

    def action_next_tab(self) -> None:
        """Make the next tab active."""
        active_tab = self.active_tab
        tabs = list(self.query(Tab))
        if not tabs:
            return
        tab_count = len(tabs)
        new_tab_index = (tabs.index(active_tab) + 1) % tab_count
        self.active = tabs[new_tab_index].id or ""
        self._scroll_active_tab()

    def action_previous_tab(self) -> None:
        """Make the previous tab active."""
        active_tab = self.active_tab
        tabs = list(self.query(Tab))
        if not tabs:
            return
        tab_count = len(tabs)
        new_tab_index = (tabs.index(active_tab) - 1) % tab_count
        self.active = tabs[new_tab_index].id or ""
        self._scroll_active_tab()


if __name__ == "__main__":
    from textual.app import App

    class TabsApp(App):
        def compose(self) -> ComposeResult:
            yield Tabs(
                "Foo",
                "bar",
                Tab("A much longer tab header"),
                Tab("Paul"),
                Tab("Jessica"),
                Tab("Duncan"),
                Tab("Chani"),
            )

            yield Tabs("a", "b")

            yield Tabs("One", "Two", "Three")

            yield Tabs()

    app = TabsApp()
    app.run()
