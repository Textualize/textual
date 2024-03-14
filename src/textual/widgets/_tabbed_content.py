from __future__ import annotations

from asyncio import gather
from dataclasses import dataclass
from itertools import zip_longest
from typing import Awaitable

from rich.repr import Result
from rich.text import Text, TextType
from typing_extensions import Final

from ..app import ComposeResult
from ..await_complete import AwaitComplete
from ..css.query import NoMatches
from ..message import Message
from ..reactive import reactive
from ..widget import Widget
from ._content_switcher import ContentSwitcher
from ._tabs import Tab, Tabs

__all__ = [
    "ContentTab",
    "TabbedContent",
    "TabPane",
]


class ContentTab(Tab):
    """A Tab with an associated content id."""

    _PREFIX: Final[str] = "--content-tab-"
    """The prefix given to the tab IDs."""

    @classmethod
    def add_prefix(cls, content_id: str) -> str:
        """Add the prefix to the given ID.

        Args:
            content_id: The ID to add the prefix to.

        Returns:
            The ID with the prefix added.
        """
        return f"{cls._PREFIX}{content_id}" if content_id else content_id

    @classmethod
    def sans_prefix(cls, content_id: str) -> str:
        """Remove the prefix from the given ID.

        Args:
            content_id: The ID to remove the prefix from.

        Returns:
            The ID with the prefix removed.
        """
        return (
            content_id[len(cls._PREFIX) :]
            if content_id.startswith(cls._PREFIX)
            else content_id
        )

    def __init__(self, label: Text, content_id: str, disabled: bool = False) -> None:
        """Initialize a ContentTab.

        Args:
            label: The label to be displayed within the tab.
            content_id: The id of the content associated with the tab.
            disabled: Is the tab disabled?
        """
        super().__init__(label, id=self.add_prefix(content_id), disabled=disabled)


class ContentTabs(Tabs):
    """A Tabs which is associated with a TabbedContent."""

    def __init__(
        self,
        *tabs: Tab | TextType,
        active: str | None = None,
        tabbed_content: TabbedContent,
    ):
        """Initialize a ContentTabs.

        Args:
            *tabs: The child tabs.
            active: ID of the tab which should be active on start.
            tabbed_content: The associated TabbedContent instance.
        """
        super().__init__(
            *tabs, active=active if active is None else ContentTab.add_prefix(active)
        )
        self.tabbed_content = tabbed_content

    def get_content_tab(self, tab_id: str) -> ContentTab:
        """Get the `ContentTab` associated with the given `TabPane` ID.

        Args:
            tab_id: The ID of the tab to get.

        Returns:
            The tab associated with that ID.
        """
        return self.query_one(f"#{ContentTab.add_prefix(tab_id)}", ContentTab)

    def disable(self, tab_id: str) -> Tab:
        """Disable the indicated tab.

        Args:
            tab_id: The ID of the [`Tab`][textual.widgets.Tab] to disable.

        Returns:
            The [`Tab`][textual.widgets.Tab] that was targeted.

        Raises:
            TabError: If there are any issues with the request.
        """
        return super().disable(ContentTab.add_prefix(tab_id))

    def enable(self, tab_id: str) -> Tab:
        """Enable the indicated tab.

        Args:
            tab_id: The ID of the [`Tab`][textual.widgets.Tab] to enable.

        Returns:
            The [`Tab`][textual.widgets.Tab] that was targeted.

        Raises:
            TabError: If there are any issues with the request.
        """
        return super().enable(ContentTab.add_prefix(tab_id))

    def hide(self, tab_id: str) -> Tab:
        """Hide the indicated tab.

        Args:
            tab_id: The ID of the [`Tab`][textual.widgets.Tab] to hide.

        Returns:
            The [`Tab`][textual.widgets.Tab] that was targeted.

        Raises:
            TabError: If there are any issues with the request.
        """
        return super().hide(ContentTab.add_prefix(tab_id))

    def show(self, tab_id: str) -> Tab:
        """Show the indicated tab.

        Args:
            tab_id: The ID of the [`Tab`][textual.widgets.Tab] to show.

        Returns:
            The [`Tab`][textual.widgets.Tab] that was targeted.

        Raises:
            TabError: If there are any issues with the request.
        """
        return super().show(ContentTab.add_prefix(tab_id))


class TabPane(Widget):
    """A container for switchable content, with additional title.

    This widget is intended to be used with [TabbedContent][textual.widgets.TabbedContent].
    """

    DEFAULT_CSS = """
    TabPane {
        height: auto;
        padding: 1 2;
    }
    """

    @dataclass
    class TabPaneMessage(Message):
        """Base class for `TabPane` messages."""

        tab_pane: TabPane
        """The `TabPane` that is he object of this message."""

        @property
        def control(self) -> TabPane:
            """The tab pane that is the object of this message.

            This is an alias for the attribute `tab_pane` and is used by the
            [`on`][textual.on] decorator.
            """
            return self.tab_pane

    @dataclass
    class Disabled(TabPaneMessage):
        """Sent when a tab pane is disabled via its reactive `disabled`."""

    @dataclass
    class Enabled(TabPaneMessage):
        """Sent when a tab pane is enabled via its reactive `disabled`."""

    def __init__(
        self,
        title: TextType,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        """Initialize a TabPane.

        Args:
            title: Title of the TabPane (will be displayed in a tab label).
            *children: Widget to go inside the TabPane.
            name: Optional name for the TabPane.
            id: Optional ID for the TabPane.
            classes: Optional initial classes for the widget.
            disabled: Whether the TabPane is disabled or not.
        """
        self._title = self.render_str(title)
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )

    def _watch_disabled(self, disabled: bool) -> None:
        """Notify the parent `TabbedContent` that a tab pane was enabled/disabled."""
        self.post_message(self.Disabled(self) if disabled else self.Enabled(self))


class TabbedContent(Widget):
    """A container with associated tabs to toggle content visibility."""

    DEFAULT_CSS = """
    TabbedContent {
        height: auto;
        &> ContentTabs {
            dock: top;
        }
    }
    """

    active: reactive[str] = reactive("", init=False)
    """The ID of the active tab, or empty string if none are active."""

    class TabActivated(Message):
        """Posted when the active tab changes."""

        ALLOW_SELECTOR_MATCH = {"pane"}
        """Additional message attributes that can be used with the [`on` decorator][textual.on]."""

        def __init__(self, tabbed_content: TabbedContent, tab: ContentTab) -> None:
            """Initialize message.

            Args:
                tabbed_content: The TabbedContent widget.
                tab: The Tab widget that was selected (contains the tab label).
            """
            self.tabbed_content = tabbed_content
            """The `TabbedContent` widget that contains the tab activated."""
            self.tab = tab
            """The `Tab` widget that was selected (contains the tab label)."""
            self.pane = tabbed_content.get_pane(tab)
            """The `TabPane` widget that was activated by selecting the tab."""
            super().__init__()

        @property
        def control(self) -> TabbedContent:
            """The `TabbedContent` widget that contains the tab activated.

            This is an alias for [`TabActivated.tabbed_content`][textual.widgets.TabbedContent.TabActivated.tabbed_content]
            and is used by the [`on`][textual.on] decorator.
            """
            return self.tabbed_content

        def __rich_repr__(self) -> Result:
            yield self.tabbed_content
            yield self.tab
            yield self.pane

    class Cleared(Message):
        """Posted when no tab pane is active.

        This can happen if all tab panes are removed or if the currently active tab
        pane is unset.
        """

        def __init__(self, tabbed_content: TabbedContent) -> None:
            """Initialize message.

            Args:
                tabbed_content: The TabbedContent widget.
            """
            self.tabbed_content = tabbed_content
            """The `TabbedContent` widget that contains the tab activated."""
            super().__init__()

        @property
        def control(self) -> TabbedContent:
            """The `TabbedContent` widget that was cleared of all tab panes.

            This is an alias for [`Cleared.tabbed_content`][textual.widgets.TabbedContent.Cleared.tabbed_content]
            and is used by the [`on`][textual.on] decorator.
            """
            return self.tabbed_content

    def __init__(
        self,
        *titles: TextType,
        initial: str = "",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        """Initialize a TabbedContent widgets.

        Args:
            *titles: Positional argument will be used as title.
            initial: The id of the initial tab, or empty string to select the first tab.
            name: The name of the button.
            id: The ID of the button in the DOM.
            classes: The CSS classes of the button.
            disabled: Whether the button is disabled or not.
        """
        self.titles = [self.render_str(title) for title in titles]
        self._tab_content: list[Widget] = []
        self._initial = initial
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

    @property
    def active_pane(self) -> TabPane | None:
        """The currently active pane, or `None` if no pane is active."""
        active = self.active
        if not active:
            return None
        return self.get_pane(self.active)

    @staticmethod
    def _set_id(content: TabPane, new_id: int) -> TabPane:
        """Set an id on the content, if not already present.

        Args:
            content: a TabPane.
            new_id: Numeric ID to make the pane ID from.

        Returns:
            The same TabPane.
        """
        if content.id is None:
            content.id = f"tab-{new_id}"
        return content

    def compose(self) -> ComposeResult:
        """Compose the tabbed content."""

        # Wrap content in a `TabPane` if required.
        pane_content = [
            self._set_id(
                (
                    content
                    if isinstance(content, TabPane)
                    else TabPane(title or self.render_str(f"Tab {index}"), content)
                ),
                index,
            )
            for index, (title, content) in enumerate(
                zip_longest(self.titles, self._tab_content), 1
            )
        ]
        # Get a tab for each pane
        tabs = [
            ContentTab(
                content._title,
                content.id or "",
                disabled=content.disabled,
            )
            for content in pane_content
        ]

        # Yield the tabs, and ensure they're linked to this TabbedContent.
        # It's important to associate the Tabs with the TabbedContent, so that this
        # TabbedContent can determine whether a message received from a Tabs instance
        # has been sent from this Tabs, or from a Tabs that may exist as a descendant
        # deeper in the DOM.
        yield ContentTabs(*tabs, active=self._initial or None, tabbed_content=self)

        # Yield the content switcher and panes
        with ContentSwitcher(initial=self._initial or None):
            yield from pane_content

    def add_pane(
        self,
        pane: TabPane,
        *,
        before: TabPane | str | None = None,
        after: TabPane | str | None = None,
    ) -> AwaitComplete:
        """Add a new pane to the tabbed content.

        Args:
            pane: The pane to add.
            before: Optional pane or pane ID to add the pane before.
            after: Optional pane or pane ID to add the pane after.

        Returns:
            An optionally awaitable object that waits for the pane to be added.

        Raises:
            Tabs.TabError: If there is a problem with the addition request.

        Note:
            Only one of `before` or `after` can be provided. If both are
            provided an exception is raised.
        """
        if isinstance(before, TabPane):
            before = before.id
        if isinstance(after, TabPane):
            after = after.id
        tabs = self.get_child_by_type(ContentTabs)
        pane = self._set_id(pane, tabs.tab_count + 1)
        assert pane.id is not None
        pane.display = False
        return AwaitComplete(
            tabs.add_tab(
                ContentTab(pane._title, pane.id),
                before=before if before is None else ContentTab.add_prefix(before),
                after=after if after is None else ContentTab.add_prefix(after),
            ),
            self.get_child_by_type(ContentSwitcher).mount(pane),
        )

    def remove_pane(self, pane_id: str) -> AwaitComplete:
        """Remove a given pane from the tabbed content.

        Args:
            pane_id: The ID of the pane to remove.

        Returns:
            An optionally awaitable object that waits for the pane to be removed
                and the Cleared message to be posted.
        """
        removal_awaitables: list[Awaitable] = [
            self.get_child_by_type(ContentTabs).remove_tab(
                ContentTab.add_prefix(pane_id)
            )
        ]
        try:
            removal_awaitables.append(
                self.get_child_by_type(ContentSwitcher)
                .get_child_by_id(pane_id)
                .remove()
            )
        except NoMatches:
            # It's possible that the content itself may have gone away via
            # other means; so allow that to be a no-op.
            pass

        async def _remove_content() -> None:
            await gather(*removal_awaitables)

        return AwaitComplete(_remove_content())

    def clear_panes(self) -> AwaitComplete:
        """Remove all the panes in the tabbed content.

        Returns:
            An optionally awaitable object which waits for all panes to be removed
                and the Cleared message to be posted.
        """
        await_clear = gather(
            self.get_child_by_type(ContentTabs).clear(),
            self.get_child_by_type(ContentSwitcher).remove_children(),
        )

        async def _clear_content() -> None:
            await await_clear

        return AwaitComplete(_clear_content())

    def compose_add_child(self, widget: Widget) -> None:
        """When using the context manager compose syntax, we want to attach nodes to the switcher.

        Args:
            widget: A Widget to add.
        """
        self._tab_content.append(widget)

    def _on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """User clicked a tab."""
        if self._is_associated_tabs(event.tabs):
            # The message is relevant, so consume it and update state accordingly.
            event.stop()
            assert event.tab.id is not None
            switcher = self.get_child_by_type(ContentSwitcher)
            switcher.current = ContentTab.sans_prefix(event.tab.id)
            with self.prevent(self.TabActivated):
                # We prevent TabbedContent.TabActivated because it is also
                # posted from the watcher for active, we're also about to
                # post it below too, which is valid as here we're reacting
                # to what the Tabs are doing. This ensures we don't get
                # doubled-up messages.
                self.active = ContentTab.sans_prefix(event.tab.id)
            self.post_message(
                TabbedContent.TabActivated(
                    tabbed_content=self,
                    tab=self.get_child_by_type(ContentTabs).get_content_tab(
                        self.active
                    ),
                )
            )

    def _on_tabs_cleared(self, event: Tabs.Cleared) -> None:
        """Called when there are no active tabs. The tabs may have been cleared,
        or they may all be hidden."""
        if self._is_associated_tabs(event.tabs):
            event.stop()
            self.get_child_by_type(ContentSwitcher).current = None
            self.active = ""

    def _is_associated_tabs(self, tabs: Tabs) -> bool:
        """Determine whether a tab is associated with this TabbedContent or not.

        A tab is "associated" with a `TabbedContent`, if it's one of the tabs that can
        be used to control it. These have a special type: `ContentTab`, and are linked
        back to this `TabbedContent` instance via a `tabbed_content` attribute.

        Args:
            tabs: The Tabs instance to check.

        Returns:
            True if the tab is associated with this `TabbedContent`.
        """
        return isinstance(tabs, ContentTabs) and tabs.tabbed_content is self

    def _watch_active(self, active: str) -> None:
        """Switch tabs when the active attributes changes."""
        with self.prevent(Tabs.TabActivated, Tabs.Cleared):
            self.get_child_by_type(ContentTabs).active = ContentTab.add_prefix(active)
        self.get_child_by_type(ContentSwitcher).current = active
        if active:
            self.post_message(
                TabbedContent.TabActivated(
                    tabbed_content=self,
                    tab=self.get_child_by_type(ContentTabs).get_content_tab(active),
                )
            )
        else:
            self.post_message(
                TabbedContent.Cleared(tabbed_content=self).set_sender(self)
            )

    @property
    def tab_count(self) -> int:
        """Total number of tabs."""
        return self.get_child_by_type(ContentTabs).tab_count

    def get_tab(self, pane_id: str | TabPane) -> Tab:
        """Get the `Tab` associated with the given ID or `TabPane`.

        Args:
            pane_id: The ID of the pane, or the pane itself.

        Returns:
            The Tab associated with the ID.

        Raises:
            ValueError: Raised if no ID was available.
        """
        if target_id := (pane_id if isinstance(pane_id, str) else pane_id.id):
            return self.get_child_by_type(ContentTabs).get_content_tab(target_id)
        raise ValueError(
            "'pane_id' must be a non-empty string or a TabPane with an id."
        )

    def get_pane(self, pane_id: str | ContentTab) -> TabPane:
        """Get the `TabPane` associated with the given ID or tab.

        Args:
            pane_id: The ID of the pane to get, or the Tab it is associated with.

        Returns:
            The `TabPane` associated with the ID or the given tab.

        Raises:
            ValueError: Raised if no ID was available.
        """
        target_id: str | None = None
        if isinstance(pane_id, ContentTab):
            target_id = (
                pane_id.id if pane_id.id is None else ContentTab.sans_prefix(pane_id.id)
            )
        else:
            target_id = pane_id
        if target_id:
            pane = self.get_child_by_type(ContentSwitcher).get_child_by_id(target_id)
            assert isinstance(pane, TabPane)
            return pane
        raise ValueError(
            "'pane_id' must be a non-empty string or a ContentTab with an id."
        )

    def _on_tabs_tab_disabled(self, event: Tabs.TabDisabled) -> None:
        """Disable the corresponding tab pane."""
        if event.tabs.parent is not self:
            return
        event.stop()
        tab_id = event.tab.id or ""
        try:
            with self.prevent(TabPane.Disabled):
                self.get_child_by_type(ContentSwitcher).get_child_by_id(
                    ContentTab.sans_prefix(tab_id), expect_type=TabPane
                ).disabled = True
        except NoMatches:
            return

    def _on_tab_pane_disabled(self, event: TabPane.Disabled) -> None:
        """Disable the corresponding tab."""
        event.stop()
        try:
            with self.prevent(Tab.Disabled):
                self.get_tab(event.tab_pane).disabled = True
        except NoMatches:
            return

    def _on_tabs_tab_enabled(self, event: Tabs.TabEnabled) -> None:
        """Enable the corresponding tab pane."""
        if event.tabs.parent is not self:
            return
        event.stop()
        tab_id = event.tab.id or ""
        try:
            with self.prevent(TabPane.Enabled):
                self.get_child_by_type(ContentSwitcher).get_child_by_id(
                    ContentTab.sans_prefix(tab_id), expect_type=TabPane
                ).disabled = False
        except NoMatches:
            return

    def _on_tab_pane_enabled(self, event: TabPane.Enabled) -> None:
        """Enable the corresponding tab."""
        event.stop()
        try:
            with self.prevent(Tab.Disabled):
                self.get_tab(event.tab_pane).disabled = False
        except NoMatches:
            return

    def disable_tab(self, tab_id: str) -> None:
        """Disables the tab with the given ID.

        Args:
            tab_id: The ID of the [`TabPane`][textual.widgets.TabPane] to disable.

        Raises:
            Tabs.TabError: If there are any issues with the request.
        """

        self.get_child_by_type(ContentTabs).disable(tab_id)

    def enable_tab(self, tab_id: str) -> None:
        """Enables the tab with the given ID.

        Args:
            tab_id: The ID of the [`TabPane`][textual.widgets.TabPane] to enable.

        Raises:
            Tabs.TabError: If there are any issues with the request.
        """

        self.get_child_by_type(ContentTabs).enable(tab_id)

    def hide_tab(self, tab_id: str) -> None:
        """Hides the tab with the given ID.

        Args:
            tab_id: The ID of the [`TabPane`][textual.widgets.TabPane] to hide.

        Raises:
            Tabs.TabError: If there are any issues with the request.
        """

        self.get_child_by_type(ContentTabs).hide(tab_id)

    def show_tab(self, tab_id: str) -> None:
        """Shows the tab with the given ID.

        Args:
            tab_id: The ID of the [`TabPane`][textual.widgets.TabPane] to show.

        Raises:
            Tabs.TabError: If there are any issues with the request.
        """

        self.get_child_by_type(ContentTabs).show(tab_id)
