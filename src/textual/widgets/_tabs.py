from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

import rich.repr
from rich.style import Style
from rich.text import Text

from textual import events
from textual.app import ComposeResult, RenderResult
from textual.await_complete import AwaitComplete
from textual.binding import Binding, BindingType
from textual.containers import Container, Horizontal, Vertical
from textual.content import Content, ContentText
from textual.css.query import NoMatches
from textual.events import Mount
from textual.geometry import Offset
from textual.message import Message
from textual.reactive import reactive
from textual.renderables.bar import Bar
from textual.visual import VisualType
from textual.widget import Widget
from textual.widgets import Static


class Underline(Widget):
    """The animated underline beneath tabs."""

    DEFAULT_CSS = """
    Underline {
        width: 1fr;
        height: 1;
        & > .underline--bar {
            color: $block-cursor-background;
            background: $foreground 10%;
        }
        &:ansi {
            text-style: dim;
        }
    }
    """

    COMPONENT_CLASSES = {"underline--bar"}
    """
    | Class | Description |
    | :- | :- |
    | `underline--bar` | Style of the bar (may be used to change the color). |
    """

    highlight_start = reactive(0)
    """First cell in highlight."""
    highlight_end = reactive(0)
    """Last cell (inclusive) in highlight."""
    show_highlight: reactive[bool] = reactive(True)
    """Flag to indicate if a highlight should be shown at all."""

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
        return (
            (self.highlight_start, self.highlight_end)
            if self.show_highlight
            else (0, 0)
        )

    def render(self) -> RenderResult:
        """Render the bar."""
        bar_style = self.get_component_rich_style("underline--bar")
        return Bar(
            highlight_range=self._highlight_range,
            highlight_style=Style.from_color(bar_style.color),
            background_style=Style.from_color(bar_style.bgcolor),
        )

    def _on_click(self, event: events.Click):
        """Catch clicks, so that the underline can activate the tabs."""
        event.stop()
        self.post_message(self.Clicked(event.screen_offset))


class Tab(Static):
    """A Widget to manage a single tab within a Tabs widget."""

    DEFAULT_CSS = """
    Tab {
        width: auto;
        height: 1;
        padding: 0 1;
        text-align: center;
        color: $foreground 50%;

        &:hover {
            color: $foreground;
        }
        &:disabled {
            color: $foreground 25%;
        }

        &.-active {
            color: $foreground;
        }
        &.-hidden {
            display: none;
        }
    }
    """

    @dataclass
    class TabMessage(Message):
        """Tab-related messages.

        These are mostly intended for internal use when interacting with `Tabs`.
        """

        tab: Tab
        """The tab that is the object of this message."""

        @property
        def control(self) -> Tab:
            """The tab that is the object of this message.

            This is an alias for the attribute `tab` and is used by the
            [`on`][textual.on] decorator.
            """
            return self.tab

    class Clicked(TabMessage):
        """A tab was clicked."""

    class Disabled(TabMessage):
        """A tab was disabled."""

    class Enabled(TabMessage):
        """A tab was enabled."""

    class Relabelled(TabMessage):
        """A tab was relabelled."""

    def __init__(
        self,
        label: ContentText,
        *,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialise a Tab.

        Args:
            label: The label to use in the tab.
            id: Optional ID for the widget.
            classes: Space separated list of class names.
            disabled: Whether the tab is disabled or not.
        """
        super().__init__(id=id, classes=classes, disabled=disabled)
        self._label: Content
        # Setter takes Text or str
        self.label = Content.from_text(label)

    @property
    def label(self) -> Content:
        """The label for the tab."""
        return self._label

    @label.setter
    def label(self, label: ContentText) -> None:
        self._label = Content.from_text(label)
        self.update(self._label)

    def update(self, content: VisualType = "") -> None:
        self.post_message(self.Relabelled(self))
        return super().update(content)

    @property
    def label_text(self) -> str:
        """Undecorated text of the label."""
        return self.label.plain

    def _on_click(self):
        """Inform the message that the tab was clicked."""
        self.post_message(self.Clicked(self))

    def _watch_disabled(self, disabled: bool) -> None:
        """Notify the parent `Tabs` that a tab was enabled/disabled."""
        self.post_message(self.Disabled(self) if disabled else self.Enabled(self))


class Tabs(Widget, can_focus=True):
    """A row of tabs."""

    DEFAULT_CSS = """
    Tabs {
        width: 100%;
        height: 2;
        &:focus {
            .underline--bar {
                background: $foreground 30%;
            }
            & .-active {
                text-style: $block-cursor-text-style;
                color: $block-cursor-foreground;
                background: $block-cursor-background;
            }
        }

        & > #tabs-scroll {
            overflow: hidden;
        }

        #tabs-list {
            width: auto;
        }
        #tabs-list-bar, #tabs-list {
            width: auto;
            height: auto;
            min-width: 100%;
            overflow: hidden hidden;
        }
        &:ansi {
            #tabs-list {
                text-style: dim;
            }
            & #tabs-list > .-active {
                text-style: not dim;
            }
            &:focus {
                #tabs-list > .-active {
                    text-style: bold not dim;
                }
            }
            & .underline--bar {
                color: ansi_bright_blue;
                background: ansi_default;
            }
            & .-active {
                color: transparent;
                background: transparent;
            }
        }
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

    class TabError(Exception):
        """Exception raised when there is an error relating to tabs."""

    class TabMessage(Message):
        """Parent class for all messages that have to do with a specific tab."""

        ALLOW_SELECTOR_MATCH = {"tab"}
        """Additional message attributes that can be used with the [`on` decorator][textual.on]."""

        def __init__(self, tabs: Tabs, tab: Tab) -> None:
            """Initialize event.

            Args:
                tabs: The Tabs widget.
                tab: The tab that is the object of this message.
            """
            self.tabs: Tabs = tabs
            """The tabs widget containing the tab."""
            self.tab: Tab = tab
            """The tab that is the object of this message."""
            super().__init__()

        @property
        def control(self) -> Tabs:
            """The tabs widget containing the tab that is the object of this message.

            This is an alias for the attribute `tabs` and is used by the
            [`on`][textual.on] decorator.
            """
            return self.tabs

        def __rich_repr__(self) -> rich.repr.Result:
            yield self.tabs
            yield self.tab

    class TabActivated(TabMessage):
        """Sent when a new tab is activated."""

    class TabDisabled(TabMessage):
        """Sent when a tab is disabled."""

    class TabEnabled(TabMessage):
        """Sent when a tab is enabled."""

    class TabHidden(TabMessage):
        """Sent when a tab is hidden."""

    class TabShown(TabMessage):
        """Sent when a tab is shown."""

    class Cleared(Message):
        """Sent when there are no active tabs.

        This can occur when Tabs are cleared, if all tabs are hidden, or if the
        currently active tab is unset.
        """

        def __init__(self, tabs: Tabs) -> None:
            """Initialize the event.

            Args:
                tabs: The tabs widget.
            """
            self.tabs: Tabs = tabs
            """The tabs widget which was cleared."""
            super().__init__()

        @property
        def control(self) -> Tabs:
            """The tabs widget which was cleared.

            This is an alias for [`Cleared.tabs`][textual.widgets.Tabs.Cleared] which
            is used by the [`on`][textual.on] decorator.
            """
            return self.tabs

        def __rich_repr__(self) -> rich.repr.Result:
            yield self.tabs

    active: reactive[str] = reactive("", init=False)
    """The ID of the active tab, or empty string if none are active."""

    def __init__(
        self,
        *tabs: Tab | ContentText,
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
            name: Optional name for the tabs widget.
            id: Optional ID for the widget.
            classes: Optional initial classes for the widget.
            disabled: Whether the widget is disabled or not.
        """
        self._tabs_counter = 0

        add_tabs = [
            (
                Tab(tab, id=f"tab-{self._new_tab_id}")
                if isinstance(tab, (str, Content, Text))
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
    def _potentially_active_tabs(self) -> list[Tab]:
        """List of all tabs that could be active.

        This list is comprised of all tabs that are shown and enabled,
        plus the active tab in case it is disabled.
        """
        return [
            tab
            for tab in self.query("#tabs-list > Tab").results(Tab)
            if ((not tab.disabled or tab is self.active_tab) and tab.display)
        ]

    @property
    def _next_active(self) -> Tab | None:
        """Next tab to make active if the active tab is removed."""
        tabs = self._potentially_active_tabs
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

    def add_tab(
        self,
        tab: Tab | ContentText,
        *,
        before: Tab | str | None = None,
        after: Tab | str | None = None,
    ) -> AwaitComplete:
        """Add a new tab to the end of the tab list.

        Args:
            tab: A new tab object, or a label (str or Text).
            before: Optional tab or tab ID to add the tab before.
            after: Optional tab or tab ID to add the tab after.

        Returns:
            An optionally awaitable object that waits for the tab to be mounted and
                internal state to be fully updated to reflect the new tab.

        Raises:
            Tabs.TabError: If there is a problem with the addition request.

        Note:
            Only one of `before` or `after` can be provided. If both are
            provided a `Tabs.TabError` will be raised.
        """

        if before and after:
            raise self.TabError("Unable to add a tab both before and after a tab")

        if isinstance(before, str):
            try:
                before = self.query_one(f"#tabs-list > #{before}", Tab)
            except NoMatches:
                raise self.TabError(
                    f"There is no tab with ID '{before}' to mount before"
                )
        elif isinstance(before, Tab) and self not in before.ancestors:
            raise self.TabError(
                "Request to add a tab before a tab that isn't part of this tab collection"
            )

        if isinstance(after, str):
            try:
                after = self.query_one(f"#tabs-list > #{after}", Tab)
            except NoMatches:
                raise self.TabError(f"There is no tab with ID '{after}' to mount after")
        elif isinstance(after, Tab) and self not in after.ancestors:
            raise self.TabError(
                "Request to add a tab after a tab that isn't part of this tab collection"
            )

        from_empty = self.tab_count == 0
        tab_widget = (
            Tab(tab, id=f"tab-{self._new_tab_id}")
            if isinstance(tab, (str, Content, Text))
            else self._auto_tab_id(tab)
        )

        mount_await = self.query_one("#tabs-list").mount(
            tab_widget, before=before, after=after
        )

        if from_empty:
            tab_widget.add_class("-active")
            activated_message = self.TabActivated(self, tab_widget)

            async def refresh_active() -> None:
                """Wait for things to be mounted before highlighting."""
                await mount_await
                self.active = tab_widget.id or ""
                self._highlight_active(animate=False)
                self.post_message(activated_message)

            return AwaitComplete(refresh_active())
        elif before or after:

            async def refresh_active() -> None:
                await mount_await
                self._highlight_active(animate=False)

            return AwaitComplete(refresh_active())

        return AwaitComplete(mount_await())

    def clear(self) -> AwaitComplete:
        """Clear all the tabs.

        Returns:
            An awaitable object that waits for the tabs to be removed.
        """
        underline = self.query_one(Underline)
        underline.highlight_start = 0
        underline.highlight_end = 0
        self.post_message(self.Cleared(self))
        self.active = ""
        return AwaitComplete(self.query("#tabs-list > Tab").remove())

    def remove_tab(self, tab_or_id: Tab | str | None) -> AwaitComplete:
        """Remove a tab.

        Args:
            tab_or_id: The Tab to remove or its id.

        Returns:
            An optionally awaitable object that waits for the tab to be removed.
        """
        if not tab_or_id:
            return AwaitComplete()

        if isinstance(tab_or_id, Tab):
            remove_tab = tab_or_id
        else:
            try:
                remove_tab = self.query_one(f"#tabs-list > #{tab_or_id}", Tab)
            except NoMatches:
                return AwaitComplete()

        if remove_tab.has_class("-active"):
            next_tab = self._next_active
        else:
            next_tab = None

        async def do_remove() -> None:
            """Perform the remove after refresh so the underline bar gets new positions."""
            await remove_tab.remove()
            if not self.query("#tabs-list > Tab"):
                self.active = ""
            elif next_tab is not None:
                self.active = next_tab.id or ""
            else:
                self._highlight_active(animate=False)

        return AwaitComplete(do_remove())

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

    def _on_mount(self, _: Mount) -> None:
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
        self.query("#tabs-list > Tab.-active").remove_class("-active")
        if active:
            try:
                active_tab = self.query_one(f"#tabs-list > #{active}", Tab)
            except NoMatches:
                return
            active_tab.add_class("-active")

            self._highlight_active(animate=previously_active != "")

            self._scroll_active_tab()
            self.post_message(self.TabActivated(self, active_tab))
        else:
            underline = self.query_one(Underline)
            underline.highlight_start = 0
            underline.highlight_end = 0
            self.post_message(self.Cleared(self))

    def _highlight_active(
        self,
        animate: bool = True,
    ) -> None:
        """Move the underline bar to under the active tab.

        Args:
            animate: Should the bar animate?
        """
        underline = self.query_one(Underline)
        try:
            _active_tab = self.query_one("#tabs-list > Tab.-active")
        except NoMatches:
            underline.show_highlight = False
            underline.highlight_start = 0
            underline.highlight_end = 0
        else:
            underline.show_highlight = True

            def move_underline(animate: bool) -> None:
                """Move the tab underline.

                Args:
                    animate: animate the underline to its new position.
                """
                try:
                    active_tab = self.query_one("#tabs-list > Tab.-active")
                except NoMatches:
                    pass
                else:
                    tab_region = active_tab.virtual_region.shrink(
                        active_tab.styles.gutter
                    )
                    start, end = tab_region.column_span
                    if animate:
                        underline.animate(
                            "highlight_start",
                            start,
                            duration=0.3,
                            level="basic",
                        )
                        underline.animate(
                            "highlight_end",
                            end,
                            duration=0.3,
                            level="basic",
                        )
                    else:
                        underline.highlight_start = start
                        underline.highlight_end = end

            if animate and self.app.animation_level != "none":
                self.set_timer(
                    0.02,
                    lambda: self.call_after_refresh(move_underline, True),
                )
            else:
                self.call_after_refresh(move_underline, False)

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
            if offset in tab.region and not tab.disabled:
                self._activate_tab(tab)
                break

    def _scroll_active_tab(self) -> None:
        """Scroll the active tab into view."""
        if self.active_tab:
            try:
                self.query_one("#tabs-scroll").scroll_to_center(
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
        """Activate the next enabled tab in the given direction.

        Tab selection wraps around. If no tab is currently active, the "next"
        tab is set to be the first and the "previous" tab is the last one.

        Args:
            direction: +1 for the next tab, -1 for the previous.
        """
        active_tab = self.active_tab
        tabs = self._potentially_active_tabs
        if not tabs:
            return
        if not active_tab:
            self.active = tabs[0 if direction == 1 else -1].id or ""
            return
        tab_count = len(tabs)
        new_tab_index = (tabs.index(active_tab) + direction) % tab_count
        self.active = tabs[new_tab_index].id or ""

    def _on_tab_disabled(self, event: Tab.Disabled) -> None:
        """Re-post the disabled message."""
        event.stop()
        self.post_message(self.TabDisabled(self, event.tab))

    def _on_tab_enabled(self, event: Tab.Enabled) -> None:
        """Re-post the enabled message."""
        event.stop()
        self.post_message(self.TabEnabled(self, event.tab))

    def _on_tab_relabelled(self, event: Tab.Relabelled) -> None:
        """Redraw the highlight when tab is relabelled."""
        event.stop()
        self._highlight_active()

    def disable(self, tab_id: str) -> Tab:
        """Disable the indicated tab.

        Args:
            tab_id: The ID of the [`Tab`][textual.widgets.Tab] to disable.

        Returns:
            The [`Tab`][textual.widgets.Tab] that was targeted.

        Raises:
            TabError: If there are any issues with the request.
        """

        try:
            tab_to_disable = self.query_one(f"#tabs-list > Tab#{tab_id}", Tab)
        except NoMatches:
            raise self.TabError(
                f"There is no tab with ID {tab_id!r} to disable."
            ) from None

        tab_to_disable.disabled = True
        return tab_to_disable

    def enable(self, tab_id: str) -> Tab:
        """Enable the indicated tab.

        Args:
            tab_id: The ID of the [`Tab`][textual.widgets.Tab] to enable.

        Returns:
            The [`Tab`][textual.widgets.Tab] that was targeted.

        Raises:
            TabError: If there are any issues with the request.
        """

        try:
            tab_to_enable = self.query_one(f"#tabs-list > Tab#{tab_id}", Tab)
        except NoMatches:
            raise self.TabError(
                f"There is no tab with ID {tab_id!r} to enable."
            ) from None

        tab_to_enable.disabled = False
        return tab_to_enable

    def hide(self, tab_id: str) -> Tab:
        """Hide the indicated tab.

        Args:
            tab_id: The ID of the [`Tab`][textual.widgets.Tab] to hide.

        Returns:
            The [`Tab`][textual.widgets.Tab] that was targeted.

        Raises:
            TabError: If there are any issues with the request.
        """

        try:
            tab_to_hide = self.query_one(f"#tabs-list > Tab#{tab_id}", Tab)
        except NoMatches:
            raise self.TabError(f"There is no tab with ID {tab_id!r} to hide.")

        if tab_to_hide.has_class("-active"):
            next_tab = self._next_active
            self.active = next_tab.id or "" if next_tab else ""
        tab_to_hide.add_class("-hidden")
        self.post_message(self.TabHidden(self, tab_to_hide).set_sender(self))
        self.call_after_refresh(self._highlight_active)
        return tab_to_hide

    def show(self, tab_id: str) -> Tab:
        """Show the indicated tab.

        Args:
            tab_id: The ID of the [`Tab`][textual.widgets.Tab] to show.

        Returns:
            The [`Tab`][textual.widgets.Tab] that was targeted.

        Raises:
            TabError: If there are any issues with the request.
        """

        try:
            tab_to_show = self.query_one(f"#tabs-list > Tab#{tab_id}", Tab)
        except NoMatches:
            raise self.TabError(f"There is no tab with ID {tab_id!r} to show.")

        tab_to_show.remove_class("-hidden")
        self.post_message(self.TabShown(self, tab_to_show).set_sender(self))
        if not self.active:
            self._activate_tab(tab_to_show)
        self.call_after_refresh(self._highlight_active)
        return tab_to_show
