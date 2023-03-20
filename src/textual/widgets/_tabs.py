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
    """
    | Class | Description |
    | :- | :- |
    | `underline-bar` | Style of the bar (may be used to change the color). |

    """

    highlight_start = reactive(0)
    """First cell in highlight."""
    highlight_end = reactive(0)
    """Last cell (inclusive) in highlight."""

    class Clicked(Message):
        """Inform ancestors the underline was clicked."""

        offset: Offset
        """The offset of the click, relative to the origin of the bar."""

        def __init__(self, offset: Offset) -> None:
            self.offset = offset
            super().__init__()

    @property
    def _highlight_range(self) -> tuple[int, int]:
        """Highlighted range for underline bar."""
        return (self.highlight_start, self.highlight_end)

    def render(self) -> RenderResult:
        """Render the bar."""
        bar_style = self.get_component_rich_style("underline--bar")
        return UnderlineBar(
            highlight_range=self._highlight_range,
            highlight_style=Style.from_color(bar_style.color),
            background_style=Style.from_color(bar_style.bgcolor),
        )

    def on_click(self, event: events.Click):
        """Catch clicks, so that the underline can activate the tabs."""
        event.stop()
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

        tab: Tab
        """The tab that was clicked."""

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
            label: The label to use in the tab.
            id: Optional ID for the widget.
        """
        self.label = Text.from_markup(label) if isinstance(label, str) else label
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
    """
    | Key(s) | Description |
    | :- | :- |
    | left | Move to the previous tab. |
    | right | Move to the next tab. |
    """

    class TabActivated(Message):
        """Sent when a new tab is activated."""

        tabs: Tabs
        """The tabs widget containing the tab."""
        tab: Tab
        """The tab that was activated."""

        def __init__(self, tabs: Tabs, tab: Tab) -> None:
            """Initialize event.

            Args:
                tabs: The Tabs widget.
                tab: The tab that was activated.
            """
            self.tabs = tabs
            self.tab = tab
            super().__init__()

        def __rich_repr__(self) -> rich.repr.Result:
            yield self.tabs
            yield self.tab

    class Cleared(Message):
        """Sent when there are no active tabs."""

        tabs: Tabs
        """The tabs widget which was cleared."""

        def __init__(self, tabs: Tabs) -> None:
            """Initialize the event.

            Args:
                tabs: The tabs widget.
            """
            self.tabs = tabs
            super().__init__()

        def __rich_repr__(self) -> rich.repr.Result:
            yield self.tabs

    active: reactive[str] = reactive("", init=False)
    """The ID of the active tab, or empty string if none are active."""

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
            active: ID of the tab which should be active on start.
            name: Optional name for the input widget.
            id: Optional ID for the widget.
            classes: Optional initial classes for the widget.
            disabled: Whether the input is disabled or not.
        """
        self._tabs_counter = 0

        add_tabs = [
            (
                Tab(tab, id=f"tab-{self._new_tab_id}")
                if isinstance(tab, (str, Text))
                else self._auto_tab_id(tab)
            )
            for tab in tabs
        ]
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self._tabs = add_tabs
        self._first_active = active

    def _auto_tab_id(self, tab: Tab) -> Tab:
        """Set an automatic ID if not supplied."""
        if tab.id is None:
            tab.id = f"tab-{self._new_tab_id}"
        return tab

    @property
    def _new_tab_id(self) -> int:
        """Get the next tab id in a sequence."""
        self._tabs_counter += 1
        return self._tabs_counter

    @property
    def tab_count(self) -> int:
        """Total number of tabs."""
        return len(self.query("#tabs-list > Tab"))

    @property
    def _next_active(self) -> Tab | None:
        """Next tab to make active if the active tab is removed."""
        tabs = list(self.query("#tabs-list > Tab").results(Tab))
        if self.active_tab is None:
            return None
        try:
            active_index = tabs.index(self.active_tab)
        except ValueError:
            return None
        del tabs[active_index]
        try:
            return tabs[active_index]
        except IndexError:
            try:
                return tabs[active_index - 1]
            except IndexError:
                pass
        return None

    def add_tab(self, tab: Tab | str | Text) -> None:
        """Add a new tab to the end of the tab list.

        Args:
            tab: A new tab object, or a label (str or Text).
        """
        from_empty = self.tab_count == 0
        tab_widget = (
            Tab(tab, id=f"tab-{self._new_tab_id}")
            if isinstance(tab, (str, Text))
            else self._auto_tab_id(tab)
        )
        mount_await = self.query_one("#tabs-list").mount(tab_widget)
        if from_empty:
            tab_widget.add_class("-active")
            self.post_message(self.TabActivated(self, tab_widget))

            async def refresh_active() -> None:
                """Wait for things to be mounted before highlighting."""
                await mount_await
                self.active = tab_widget.id or ""
                self._highlight_active(animate=False)

            self.call_after_refresh(refresh_active)

    def clear(self) -> None:
        """Clear all the tabs."""
        underline = self.query_one(Underline)
        underline.highlight_start = 0
        underline.highlight_end = 0
        self.query("#tabs-list > Tab").remove()
        self.post_message(self.Cleared(self))

    def remove_tab(self, tab_or_id: Tab | str | None) -> None:
        """Remove a tab.

        Args:
            tab_id: The Tab's id.
        """
        if tab_or_id is None:
            return
        if isinstance(tab_or_id, Tab):
            remove_tab = tab_or_id
        else:
            try:
                remove_tab = self.query_one(f"#tabs-list > #{tab_or_id}", Tab)
            except NoMatches:
                return
        removing_active_tab = remove_tab.has_class("-active")

        next_tab = self._next_active
        if next_tab is None:
            self.post_message(self.Cleared(self))
        else:
            self.post_message(self.TabActivated(self, next_tab))

        async def do_remove() -> None:
            """Perform the remove after refresh so the underline bar gets new positions."""
            await remove_tab.remove()
            if removing_active_tab:
                if next_tab is not None:
                    next_tab.add_class("-active")
                self.call_after_refresh(self._highlight_active, animate=True)

        self.call_after_refresh(do_remove)

    def validate_active(self, active: str) -> str:
        """Check id assigned to active attribute is a valid tab."""
        if active and not self.query(f"#tabs-list > #{active}"):
            raise ValueError(f"No Tab with id {active!r}")
        return active

    @property
    def active_tab(self) -> Tab | None:
        """The currently active tab, or None if there are no active tabs."""
        try:
            return self.query_one("#tabs-list Tab.-active", Tab)
        except NoMatches:
            return None

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
        """Handle a change to the active tab."""
        if active:
            active_tab = self.query_one(f"#tabs-list > #{active}", Tab)
            self.query("#tabs-list > Tab.-active").remove_class("-active")
            active_tab.add_class("-active")
            self._highlight_active(animate=previously_active != "")
            self.post_message(self.TabActivated(self, active_tab))
        else:
            underline = self.query_one(Underline)
            underline.highlight_start = 0
            underline.highlight_end = 0
            self.post_message(self.Cleared(self))

    def _highlight_active(self, animate: bool = True) -> None:
        """Move the underline bar to under the active tab.

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
        """Activate a tab that was clicked."""
        self.focus()
        event.stop()
        self._activate_tab(event.tab)

    def _activate_tab(self, tab: Tab) -> None:
        """Activate a tab.

        Args:
            tab: The Tab that was clicked.
        """
        self.query("#tabs-list Tab.-active").remove_class("-active")
        tab.add_class("-active")
        self.active = tab.id or ""
        self.query_one("#tabs-scroll").scroll_to_widget(tab, force=True)

    def _on_underline_clicked(self, event: Underline.Clicked) -> None:
        """The underline was clicked.

        Activate the tab above to make a larger clickable area.

        Args:
            event: The Underline.Clicked event.
        """
        event.stop()
        offset = event.offset + (0, -1)
        self.focus()
        for tab in self.query(Tab):
            if offset in tab.region:
                self._activate_tab(tab)
                break

    def _scroll_active_tab(self) -> None:
        """Scroll the active tab into view."""
        if self.active_tab:
            try:
                self.query_one("#tabs-scroll").scroll_to_widget(
                    self.active_tab, force=True
                )
            except NoMatches:
                pass

    def _on_resize(self):
        """Make the active tab visible on resize."""
        self._highlight_active(animate=False)
        self._scroll_active_tab()

    def action_next_tab(self) -> None:
        """Make the next tab active."""
        self._move_tab(+1)

    def action_previous_tab(self) -> None:
        """Make the previous tab active."""
        self._move_tab(-1)

    def _move_tab(self, direction: int) -> None:
        """Activate the next tab.

        Args:
            direction: +1 for the next tab, -1 for the previous.
        """
        active_tab = self.active_tab
        if active_tab is None:
            return
        tabs = list(self.query(Tab))
        if not tabs:
            return
        tab_count = len(tabs)
        new_tab_index = (tabs.index(active_tab) + direction) % tab_count
        self.active = tabs[new_tab_index].id or ""
        self._scroll_active_tab()
