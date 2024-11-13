from __future__ import annotations

import pytest

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Tab, Tabs
from textual.widgets._tabs import Underline


async def test_tab_label():
    """It should be possible to access a tab's label."""
    assert Tab("Pilot").label_text == "Pilot"


async def test_tab_relabel():
    """It should be possible to relabel a tab."""
    tab = Tab("Pilot")
    assert tab.label_text == "Pilot"
    tab.label = "Aeryn"
    assert tab.label_text == "Aeryn"


async def test_compose_empty_tabs():
    """It should be possible to create an empty Tabs."""

    class TabsApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs()

    async with TabsApp().run_test() as pilot:
        assert pilot.app.query_one(Tabs).tab_count == 0
        assert pilot.app.query_one(Tabs).active_tab is None


async def test_compose_tabs_from_strings():
    """It should be possible to create a Tabs from some strings."""

    class TabsApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs("John", "Aeryn", "Moya", "Pilot")

    async with TabsApp().run_test() as pilot:
        tabs = pilot.app.query_one(Tabs)
        assert tabs.tab_count == 4
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"


async def test_compose_tabs_from_tabs():
    """It should be possible to create a Tabs from some Tabs."""

    class TabsApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs(
                Tab("John"),
                Tab("Aeryn"),
                Tab("Moya"),
                Tab("Pilot"),
            )

    async with TabsApp().run_test() as pilot:
        tabs = pilot.app.query_one(Tabs)
        assert tabs.tab_count == 4
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"


async def test_add_tabs_later():
    """It should be possible to add tabs later on in the app's cycle."""

    class TabsApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs()

    async with TabsApp().run_test() as pilot:
        tabs = pilot.app.query_one(Tabs)
        assert tabs.tab_count == 0
        assert tabs.active_tab is None
        await tabs.add_tab("John")
        assert tabs.tab_count == 1
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"
        await tabs.add_tab("Aeryn")
        assert tabs.tab_count == 2
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"


async def test_add_tab_before():
    """It should be possible to add a tab before another tab."""

    class TabsApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs("Pilot")

    async with TabsApp().run_test() as pilot:
        tabs = pilot.app.query_one(Tabs)
        assert tabs.tab_count == 1
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"
        assert tabs.active == "tab-1"
        await tabs.add_tab("John", before="tab-1")
        assert tabs.tab_count == 2
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"
        assert tabs.active == "tab-1"
        await tabs.add_tab("John", before=tabs.active_tab)
        assert tabs.tab_count == 3
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"
        assert tabs.active == "tab-1"


async def test_add_tab_before_badly():
    """Test exceptions from badly adding a tab before another."""

    class TabsApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs("Pilot")

    async with TabsApp().run_test() as pilot:
        tabs = pilot.app.query_one(Tabs)
        assert tabs.tab_count == 1
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"
        assert tabs.active == "tab-1"
        with pytest.raises(Tabs.TabError):
            tabs.add_tab("John", before="this-is-not-a-tab")
        assert tabs.tab_count == 1
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"
        assert tabs.active == "tab-1"
        with pytest.raises(Tabs.TabError):
            tabs.add_tab("John", before=Tab("I just made this up"))
        assert tabs.tab_count == 1
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"
        assert tabs.active == "tab-1"


async def test_add_tab_after():
    """It should be possible to add a tab after another tab."""

    class TabsApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs("Pilot")

    async with TabsApp().run_test() as pilot:
        tabs = pilot.app.query_one(Tabs)
        assert tabs.tab_count == 1
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"
        assert tabs.active == "tab-1"
        await tabs.add_tab("John", after="tab-1")
        assert tabs.tab_count == 2
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"
        assert tabs.active == "tab-1"
        await tabs.add_tab("John", after=tabs.active_tab)
        assert tabs.tab_count == 3
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"
        assert tabs.active == "tab-1"


async def test_add_tab_after_badly():
    """Test exceptions from badly adding a tab after another."""

    class TabsApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs("Pilot")

    async with TabsApp().run_test() as pilot:
        tabs = pilot.app.query_one(Tabs)
        assert tabs.tab_count == 1
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"
        assert tabs.active == "tab-1"
        with pytest.raises(Tabs.TabError):
            tabs.add_tab("John", after="this-is-not-a-tab")
        assert tabs.tab_count == 1
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"
        assert tabs.active == "tab-1"
        with pytest.raises(Tabs.TabError):
            tabs.add_tab("John", after=Tab("I just made this up"))
        assert tabs.tab_count == 1
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"
        assert tabs.active == "tab-1"


async def test_add_tab_before_and_after():
    """Attempting to add a tab before and after another is an error."""

    class TabsApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs("Pilot")

    async with TabsApp().run_test() as pilot:
        tabs = pilot.app.query_one(Tabs)
        assert tabs.tab_count == 1
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"
        assert tabs.active == "tab-1"
        with pytest.raises(Tabs.TabError):
            tabs.add_tab("John", before="tab-1", after="tab-1")


async def test_remove_tabs():
    """It should be possible to remove tabs."""

    class TabsApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs("John", "Aeryn", "Moya", "Pilot")

    async with TabsApp().run_test() as pilot:
        tabs = pilot.app.query_one(Tabs)
        assert tabs.tab_count == 4
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"

        await tabs.remove_tab("tab-1")
        assert tabs.tab_count == 3
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-2"

        await tabs.remove_tab(tabs.query_one("#tab-2", Tab))
        assert tabs.tab_count == 2
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-3"

        await tabs.remove_tab("tab-does-not-exist")
        assert tabs.tab_count == 2
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-3"

        await tabs.remove_tab(None)
        assert tabs.tab_count == 2
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-3"

        await tabs.remove_tab("tab-3")
        await tabs.remove_tab("tab-4")
        assert tabs.tab_count == 0
        assert tabs.active_tab is None


async def test_remove_tabs_reversed():
    """It should be possible to remove tabs."""

    class TabsApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs("John", "Aeryn", "Moya", "Pilot")

    async with TabsApp().run_test() as pilot:
        tabs = pilot.app.query_one(Tabs)
        assert tabs.tab_count == 4
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"

        await tabs.remove_tab("tab-4")
        assert tabs.tab_count == 3
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"

        await tabs.remove_tab("tab-3")
        assert tabs.tab_count == 2
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"

        await tabs.remove_tab("tab-2")
        assert tabs.tab_count == 1
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"

        await tabs.remove_tab("tab-1")
        assert tabs.tab_count == 0
        assert tabs.active_tab is None


async def test_clear_tabs():
    """It should be possible to clear all tabs."""

    class TabsApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs("John", "Aeryn", "Moya", "Pilot")

    async with TabsApp().run_test() as pilot:
        tabs = pilot.app.query_one(Tabs)
        assert tabs.tab_count == 4
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"
        await tabs.clear()
        assert tabs.tab_count == 0
        assert tabs.active_tab is None


async def test_change_active_from_code():
    """It should be possible to change the active tab from code.."""

    class TabsApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs("John", "Aeryn", "Moya", "Pilot")

    async with TabsApp().run_test() as pilot:
        tabs = pilot.app.query_one(Tabs)
        assert tabs.tab_count == 4
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"
        assert tabs.active == tabs.active_tab.id

        tabs.active = "tab-2"
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-2"
        assert tabs.active == tabs.active_tab.id

        tabs.active = ""
        assert tabs.active_tab is None


async def test_navigate_tabs_with_keyboard():
    """It should be possible to navigate tabs with the keyboard."""

    class TabsApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs("John", "Aeryn", "Moya", "Pilot")

    async with TabsApp().run_test() as pilot:
        tabs = pilot.app.query_one(Tabs)
        assert tabs.tab_count == 4
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"
        assert tabs.active == tabs.active_tab.id

        await pilot.press("right")
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-2"
        assert tabs.active == tabs.active_tab.id

        await pilot.press("left")
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"
        assert tabs.active == tabs.active_tab.id

        await pilot.press(*(["left"] * tabs.tab_count))
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"
        assert tabs.active == tabs.active_tab.id


async def test_navigate_empty_tabs_with_keyboard():
    """It should be possible to navigate an empty tabs with the keyboard."""

    class TabsApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs()

    async with TabsApp().run_test() as pilot:
        tabs = pilot.app.query_one(Tabs)
        assert tabs.tab_count == 0
        assert tabs.active_tab is None
        assert tabs.active == ""

        await pilot.press("right")
        assert tabs.active_tab is None
        assert tabs.active == ""

        await pilot.press("left")
        assert tabs.active_tab is None
        assert tabs.active == ""


async def test_navigate_tabs_with_mouse():
    """It should be possible to navigate tabs with the mouse."""

    class TabsApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs("John", "Aeryn", "Moya", "Pilot")

    async with TabsApp().run_test() as pilot:
        tabs = pilot.app.query_one(Tabs)
        assert tabs.tab_count == 4
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"

        await pilot.click("#tab-2")
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-2"

        await pilot.click("Underline", offset=(2, 0))
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "tab-1"


class TabsMessageCatchApp(App[None]):
    def __init__(self) -> None:
        super().__init__()
        self.intended_handlers: list[str] = []

    def compose(self) -> ComposeResult:
        yield Tabs("John", "Aeryn", "Moya", "Pilot")

    @on(Tabs.Cleared)
    @on(Tabs.TabActivated)
    @on(Underline.Clicked)
    @on(Tab.Clicked)
    def log_message(
        self, event: Tabs.Cleared | Tabs.TabActivated | Underline.Clicked | Tab.Clicked
    ) -> None:
        self.intended_handlers.append(event.handler_name)

    @on(Tabs.TabActivated)
    @on(Tabs.Cleared)
    def check_control(self, event: Tabs.TabActivated) -> None:
        assert event.control is event.tabs


async def test_startup_messages():
    """On startup there should be a tab activated message."""
    async with TabsMessageCatchApp().run_test() as pilot:
        assert pilot.app.intended_handlers == ["on_tabs_tab_activated"]


async def test_change_tab_with_code_messages():
    """Changing tab in code should result in an activated tab message."""
    async with TabsMessageCatchApp().run_test() as pilot:
        pilot.app.query_one(Tabs).active = "tab-2"
        await pilot.pause()
        assert pilot.app.intended_handlers == [
            "on_tabs_tab_activated",
            "on_tabs_tab_activated",
        ]


async def test_remove_tabs_messages():
    """Removing tabs should result in various messages."""
    async with TabsMessageCatchApp().run_test() as pilot:
        tabs = pilot.app.query_one(Tabs)
        for n in range(4):
            await tabs.remove_tab(f"tab-{n+1}")

        await pilot.pause()
        assert pilot.app.intended_handlers == [
            "on_tabs_tab_activated",
            "on_tabs_tab_activated",
            "on_tabs_tab_activated",
            "on_tabs_tab_activated",
            "on_tabs_cleared",
        ]


async def test_reverse_remove_tabs_messages():
    """Removing tabs should result in various messages."""
    async with TabsMessageCatchApp().run_test() as pilot:
        tabs = pilot.app.query_one(Tabs)
        for n in reversed(range(4)):
            await tabs.remove_tab(f"tab-{n+1}")

        await pilot.pause()
        assert pilot.app.intended_handlers == [
            "on_tabs_tab_activated",
            "on_tabs_cleared",
        ]


async def test_keyboard_navigation_messages():
    """Keyboard navigation should result in the expected messages."""
    async with TabsMessageCatchApp().run_test() as pilot:
        await pilot.press("right")
        await pilot.pause()
        await pilot.press("left")
        await pilot.pause()
        assert pilot.app.intended_handlers == [
            "on_tabs_tab_activated",
            "on_tabs_tab_activated",
            "on_tabs_tab_activated",
        ]


async def test_mouse_navigation_messages():
    """Mouse navigation should result in the expected messages."""
    async with TabsMessageCatchApp().run_test() as pilot:
        await pilot.click("#tab-2")
        await pilot.pause()
        await pilot.click("Underline", offset=(2, 0))
        await pilot.pause()
        assert pilot.app.intended_handlers == [
            "on_tabs_tab_activated",
            "on_tabs_tab_activated",
            "on_tabs_tab_activated",
        ]


async def test_disabled_tab_is_not_activated_by_clicking_underline():
    """Regression test for https://github.com/Textualize/textual/issues/4701"""

    class DisabledTabApp(App):
        def compose(self) -> ComposeResult:
            yield Tabs(
                Tab("Enabled", id="enabled"),
                Tab("Disabled", id="disabled", disabled=True),
            )

    app = DisabledTabApp()
    async with app.run_test() as pilot:
        # Click the underline beneath the disabled tab
        await pilot.click(Tabs, offset=(14, 2))
        tabs = pilot.app.query_one(Tabs)
        assert tabs.active_tab is not None
        assert tabs.active_tab.id == "enabled"
