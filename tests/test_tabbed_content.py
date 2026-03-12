from __future__ import annotations

import pytest

from textual.app import App, ComposeResult
from textual.reactive import var
from textual.widgets import (
    Button,
    Footer,
    Input,
    Label,
    Tab,
    TabbedContent,
    TabPane,
    Tabs,
)
from textual.widgets._tabbed_content import ContentTab


async def test_tabbed_content_switch_via_ui():
    """Check tab navigation via the user interface."""

    class TabbedApp(App):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                with TabPane("foo", id="foo"):
                    yield Label("Foo", id="foo-label")
                with TabPane("bar", id="bar"):
                    yield Label("Bar", id="bar-label")
                with TabPane("baz", id="baz"):
                    yield Label("Baz", id="baz-label")

    app = TabbedApp()
    async with app.run_test() as pilot:
        tabbed_content = app.query_one(TabbedContent)
        # Check first tab
        assert tabbed_content.active == "foo"
        assert tabbed_content.active_pane.id == "foo"
        await pilot.pause()
        assert app.query_one("#foo-label").region
        assert not app.query_one("#bar-label").region
        assert not app.query_one("#baz-label").region

        # Click second tab
        await pilot.click(f"Tab#{ContentTab.add_prefix('bar')}")
        assert tabbed_content.active == "bar"
        assert tabbed_content.active_pane.id == "bar"
        await pilot.pause()
        assert not app.query_one("#foo-label").region
        assert app.query_one("#bar-label").region
        assert not app.query_one("#baz-label").region

        # Click third tab
        await pilot.click(f"Tab#{ContentTab.add_prefix('baz')}")
        assert tabbed_content.active == "baz"
        assert tabbed_content.active_pane.id == "baz"
        await pilot.pause()
        assert not app.query_one("#foo-label").region
        assert not app.query_one("#bar-label").region
        assert app.query_one("#baz-label").region

        # Press left
        await pilot.press("left")
        assert tabbed_content.active == "bar"
        await pilot.pause()
        assert not app.query_one("#foo-label").region
        assert app.query_one("#bar-label").region
        assert not app.query_one("#baz-label").region

        # Press right
        await pilot.press("right")
        assert tabbed_content.active == "baz"
        await pilot.pause()
        assert not app.query_one("#foo-label").region
        assert not app.query_one("#bar-label").region
        assert app.query_one("#baz-label").region


async def test_tabbed_content_switch_via_code():
    """Check tab navigation via code."""

    class TabbedApp(App):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                with TabPane("foo", id="foo"):
                    yield Label("Foo", id="foo-label")
                with TabPane("bar", id="bar"):
                    yield Label("Bar", id="bar-label")
                with TabPane("baz", id="baz"):
                    yield Label("Baz", id="baz-label")

    app = TabbedApp()
    async with app.run_test() as pilot:
        tabbed_content = app.query_one(TabbedContent)

        # Check first tab
        assert tabbed_content.active == "foo"
        assert app.query_one("#foo-label").region
        assert not app.query_one("#bar-label").region
        assert not app.query_one("#baz-label").region

        # Click second tab
        tabbed_content.active = "bar"
        await pilot.pause()
        assert not app.query_one("#foo-label").region
        assert app.query_one("#bar-label").region
        assert not app.query_one("#baz-label").region

        # Click third tab
        tabbed_content.active = "baz"
        await pilot.pause()
        assert not app.query_one("#foo-label").region
        assert not app.query_one("#bar-label").region
        assert app.query_one("#baz-label").region

        # Check fail with non existent tab
        with pytest.raises(ValueError):
            tabbed_content.active = "X"


async def test_unsetting_tabbed_content_active():
    """Check that setting `TabbedContent.active = ""` unsets active tab."""

    messages = []

    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent(initial="bar"):
                with TabPane("foo", id="foo"):
                    yield Label("Foo", id="foo-label")
                with TabPane("bar", id="bar"):
                    yield Label("Bar", id="bar-label")
                with TabPane("baz", id="baz"):
                    yield Label("Baz", id="baz-label")

        def on_tabbed_content_cleared(self, event: TabbedContent.Cleared) -> None:
            messages.append(event)

    app = TabbedApp()
    async with app.run_test() as pilot:
        tabbed_content = app.query_one(TabbedContent)
        assert bool(tabbed_content.active)
        tabbed_content.active = ""
        await pilot.pause()
        assert len(messages) == 1
        assert isinstance(messages[0], TabbedContent.Cleared)


async def test_tabbed_content_initial():
    """Checked tabbed content with non-default tab."""

    class TabbedApp(App):
        def compose(self) -> ComposeResult:
            with TabbedContent(initial="bar"):
                with TabPane("foo", id="foo"):
                    yield Label("Foo", id="foo-label")
                with TabPane("bar", id="bar"):
                    yield Label("Bar", id="bar-label")
                with TabPane("baz", id="baz"):
                    yield Label("Baz", id="baz-label")

    app = TabbedApp()
    async with app.run_test():
        tabbed_content = app.query_one(TabbedContent)
        assert tabbed_content.active == "bar"

        # Check only bar is visible
        assert not app.query_one("#foo-label").region
        assert app.query_one("#bar-label").region
        assert not app.query_one("#baz-label").region


async def test_tabbed_content_messages():
    class TabbedApp(App):
        activation_history: list[Tab] = []

        def compose(self) -> ComposeResult:
            with TabbedContent():
                with TabPane("foo", id="foo"):
                    yield Label("Foo", id="foo-label")
                with TabPane("bar", id="bar"):
                    yield Label("Bar", id="bar-label")
                with TabPane("baz", id="baz"):
                    yield Label("Baz", id="baz-label")

        def on_tabbed_content_tab_activated(
            self, event: TabbedContent.TabActivated
        ) -> None:
            self.activation_history.append(event.tab)

    app = TabbedApp()
    async with app.run_test() as pilot:
        tabbed_content = app.query_one(TabbedContent)
        tabbed_content.active = "bar"
        await pilot.pause()
        assert app.activation_history == [
            # foo was originally activated.
            app.query_one(TabbedContent).get_tab("foo"),
            # then we did bar "by hand"
            app.query_one(TabbedContent).get_tab("bar"),
        ]


async def test_tabbed_content_add_later_from_empty():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            yield TabbedContent()

    async with TabbedApp().run_test() as pilot:
        tabbed_content = pilot.app.query_one(TabbedContent)
        assert tabbed_content.active == ""
        assert tabbed_content.tab_count == 0
        await tabbed_content.add_pane(TabPane("Test 1", id="test-1"))
        assert tabbed_content.tab_count == 1
        assert tabbed_content.active == "test-1"
        await tabbed_content.add_pane(TabPane("Test 2", id="test-2"))
        assert tabbed_content.tab_count == 2
        assert tabbed_content.active == "test-1"


async def test_tabbed_content_add_later_from_composed():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield TabPane("Test 1", id="initial-1")
                yield TabPane("Test 2", id="initial-2")
                yield TabPane("Test 3", id="initial-3")

    async with TabbedApp().run_test() as pilot:
        tabbed_content = pilot.app.query_one(TabbedContent)
        assert tabbed_content.tab_count == 3
        assert tabbed_content.active == "initial-1"
        await tabbed_content.add_pane(TabPane("Test 4", id="test-1"))
        assert tabbed_content.tab_count == 4
        assert tabbed_content.active == "initial-1"
        await tabbed_content.add_pane(TabPane("Test 5", id="test-2"))
        assert tabbed_content.tab_count == 5
        assert tabbed_content.active == "initial-1"


async def test_tabbed_content_add_before_id():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield TabPane("Test 1", id="initial-1")

    async with TabbedApp().run_test() as pilot:
        tabbed_content = pilot.app.query_one(TabbedContent)
        assert tabbed_content.tab_count == 1
        assert tabbed_content.active == "initial-1"
        await tabbed_content.add_pane(TabPane("Added", id="new-1"), before="initial-1")
        assert tabbed_content.tab_count == 2
        assert tabbed_content.active == "initial-1"
        assert [
            ContentTab.sans_prefix(tab.id) for tab in tabbed_content.query(Tab)
        ] == [
            "new-1",
            "initial-1",
        ]


async def test_tabbed_content_add_before_pane():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield TabPane("Test 1", id="initial-1")

    async with TabbedApp().run_test() as pilot:
        tabbed_content = pilot.app.query_one(TabbedContent)
        assert tabbed_content.tab_count == 1
        assert tabbed_content.active == "initial-1"
        await tabbed_content.add_pane(
            TabPane("Added", id="new-1"),
            before=pilot.app.query_one("TabPane#initial-1", TabPane),
        )
        assert tabbed_content.tab_count == 2
        assert tabbed_content.active == "initial-1"
        assert [
            ContentTab.sans_prefix(tab.id)
            for tab in tabbed_content.query(Tab).results(Tab)
        ] == [
            "new-1",
            "initial-1",
        ]


async def test_tabbed_content_add_before_badly():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield TabPane("Test 1", id="initial-1")

    async with TabbedApp().run_test() as pilot:
        tabbed_content = pilot.app.query_one(TabbedContent)
        assert tabbed_content.tab_count == 1
        assert tabbed_content.active == "initial-1"
        with pytest.raises(Tabs.TabError):
            await tabbed_content.add_pane(
                TabPane("Added", id="new-1"), before="unknown-1"
            )


async def test_tabbed_content_add_after():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield TabPane("Test 1", id="initial-1")

    async with TabbedApp().run_test() as pilot:
        tabbed_content = pilot.app.query_one(TabbedContent)
        assert tabbed_content.tab_count == 1
        assert tabbed_content.active == "initial-1"
        await tabbed_content.add_pane(TabPane("Added", id="new-1"), after="initial-1")
        assert tabbed_content.tab_count == 2
        assert tabbed_content.active == "initial-1"
        assert [
            ContentTab.sans_prefix(tab.id)
            for tab in tabbed_content.query(Tab).results(Tab)
        ] == [
            "initial-1",
            "new-1",
        ]


async def test_tabbed_content_add_after_pane():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield TabPane("Test 1", id="initial-1")

    async with TabbedApp().run_test() as pilot:
        tabbed_content = pilot.app.query_one(TabbedContent)
        assert tabbed_content.tab_count == 1
        assert tabbed_content.active == "initial-1"
        await tabbed_content.add_pane(
            TabPane("Added", id="new-1"),
            after=pilot.app.query_one("TabPane#initial-1", TabPane),
        )
        await pilot.pause()
        assert tabbed_content.tab_count == 2
        assert tabbed_content.active == "initial-1"
        assert [
            ContentTab.sans_prefix(tab.id)
            for tab in tabbed_content.query(Tab).results(Tab)
        ] == [
            "initial-1",
            "new-1",
        ]


async def test_tabbed_content_add_after_badly():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield TabPane("Test 1", id="initial-1")

    async with TabbedApp().run_test() as pilot:
        tabbed_content = pilot.app.query_one(TabbedContent)
        assert tabbed_content.tab_count == 1
        assert tabbed_content.active == "initial-1"
        with pytest.raises(Tabs.TabError):
            await tabbed_content.add_pane(
                TabPane("Added", id="new-1"), after="unknown-1"
            )


async def test_tabbed_content_add_before_and_after():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield TabPane("Test 1", id="initial-1")

    async with TabbedApp().run_test() as pilot:
        tabbed_content = pilot.app.query_one(TabbedContent)
        assert tabbed_content.tab_count == 1
        assert tabbed_content.active == "initial-1"
        with pytest.raises(Tabs.TabError):
            await tabbed_content.add_pane(
                TabPane("Added", id="new-1"), before="initial-1", after="initial-1"
            )


async def test_tabbed_content_removal():
    class TabbedApp(App[None]):
        cleared: var[int] = var(0)

        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield TabPane("Test 1", id="initial-1")
                yield TabPane("Test 2", id="initial-2")
                yield TabPane("Test 3", id="initial-3")

        def on_tabbed_content_cleared(self) -> None:
            self.cleared += 1

    async with TabbedApp().run_test() as pilot:
        tabbed_content = pilot.app.query_one(TabbedContent)
        assert tabbed_content.tab_count == 3
        assert pilot.app.cleared == 0
        assert tabbed_content.active == "initial-1"
        await tabbed_content.remove_pane("initial-1")
        await pilot.pause()
        assert tabbed_content.tab_count == 2
        assert pilot.app.cleared == 0
        assert tabbed_content.active == "initial-2"
        await tabbed_content.remove_pane("initial-2")
        await pilot.pause()
        assert tabbed_content.tab_count == 1
        assert pilot.app.cleared == 0
        assert tabbed_content.active == "initial-3"
        await tabbed_content.remove_pane("initial-3")
        await pilot.pause()
        assert tabbed_content.tab_count == 0
        assert pilot.app.cleared == 1
        assert tabbed_content.active == ""


async def test_tabbed_content_reversed_removal():
    class TabbedApp(App[None]):
        cleared: var[int] = var(0)

        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield TabPane("Test 1", id="initial-1")
                yield TabPane("Test 2", id="initial-2")
                yield TabPane("Test 3", id="initial-3")

        def on_tabbed_content_cleared(self) -> None:
            self.cleared += 1

    async with TabbedApp().run_test() as pilot:
        tabbed_content = pilot.app.query_one(TabbedContent)
        assert tabbed_content.tab_count == 3
        assert pilot.app.cleared == 0
        assert tabbed_content.active == "initial-1"
        await tabbed_content.remove_pane("initial-3")
        await pilot.pause()
        assert tabbed_content.tab_count == 2
        assert pilot.app.cleared == 0
        assert tabbed_content.active == "initial-1"
        await tabbed_content.remove_pane("initial-2")
        await pilot.pause()
        assert tabbed_content.tab_count == 1
        assert pilot.app.cleared == 0
        assert tabbed_content.active == "initial-1"
        await tabbed_content.remove_pane("initial-1")
        await pilot.pause()
        assert tabbed_content.tab_count == 0
        assert pilot.app.cleared == 1
        assert tabbed_content.active == ""


async def test_tabbed_content_clear():
    class TabbedApp(App[None]):
        cleared: var[int] = var(0)

        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield TabPane("Test 1", id="initial-1")
                yield TabPane("Test 2", id="initial-2")
                yield TabPane("Test 3", id="initial-3")

        def on_tabbed_content_cleared(self) -> None:
            self.cleared += 1

    async with TabbedApp().run_test() as pilot:
        tabbed_content = pilot.app.query_one(TabbedContent)
        assert tabbed_content.tab_count == 3
        assert tabbed_content.active == "initial-1"
        assert pilot.app.cleared == 0
        await tabbed_content.clear_panes()
        await pilot.pause()
        assert tabbed_content.tab_count == 0
        assert tabbed_content.active == ""
        assert pilot.app.cleared == 1


async def test_disabling_does_not_deactivate_tab():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield Label("tab-1")

        def on_mount(self) -> None:
            self.query_one(TabbedContent).get_tab("tab-1").disabled = True

    app = TabbedApp()
    async with app.run_test():
        assert app.query_one(TabbedContent).active == "tab-1"


async def test_disabled_tab_cannot_be_clicked():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield Label("tab-1")
                yield Label("tab-2")

        def on_mount(self) -> None:
            self.query_one(TabbedContent).get_tab("tab-2").disabled = True

    app = TabbedApp()
    async with app.run_test() as pilot:
        await pilot.click(f"Tab#{ContentTab.add_prefix('tab-2')}")
        assert app.query_one(TabbedContent).active == "tab-1"


async def test_disabling_via_tabbed_content():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield Label("tab-1")
                yield Label("tab-2")

        def on_mount(self) -> None:
            self.query_one(TabbedContent).disable_tab("tab-2")

    app = TabbedApp()
    async with app.run_test() as pilot:
        await pilot.click(f"Tab#{ContentTab.add_prefix('tab-2')}")
        assert app.query_one(TabbedContent).active == "tab-1"


async def test_disabling_via_tab_pane():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield Label("tab-1")
                yield Label("tab-2")

        def on_mount(self) -> None:
            self.query_one("TabPane#tab-2").disabled = True

    app = TabbedApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.click(f"Tab#{ContentTab.add_prefix('tab-2')}")
        assert app.query_one(TabbedContent).active == "tab-1"


async def test_creating_disabled_tab():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                with TabPane("first"):
                    yield Label("hello")
                with TabPane("second", disabled=True):
                    yield Label("world")

    app = TabbedApp()
    async with app.run_test() as pilot:
        await pilot.click(f"Tab#{ContentTab.add_prefix('tab-2')}")
        assert app.query_one(TabbedContent).active == "tab-1"


async def test_navigation_around_disabled_tabs():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield Label("tab-1")
                yield Label("tab-2")
                yield Label("tab-3")
                yield Label("tab-4")

        def on_mount(self) -> None:
            self.query_one(TabbedContent).get_tab("tab-1").disabled = True
            self.query_one(TabbedContent).get_tab("tab-3").disabled = True

    app = TabbedApp()
    async with app.run_test() as pilot:
        tabbed_conent = app.query_one(TabbedContent)
        tabs = app.query_one(Tabs)
        assert tabbed_conent.active == "tab-1"
        tabs.action_next_tab()
        await pilot.pause()
        assert tabbed_conent.active == "tab-2"
        tabs.action_next_tab()
        await pilot.pause()
        assert tabbed_conent.active == "tab-4"
        tabs.action_next_tab()
        await pilot.pause()
        assert tabbed_conent.active == "tab-2"
        tabs.action_previous_tab()
        await pilot.pause()
        assert tabbed_conent.active == "tab-4"


async def test_reenabling_tab():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield Label("tab-1")
                yield Label("tab-2")

        def on_mount(self) -> None:
            self.query_one(TabbedContent).get_tab("tab-2").disabled = True

        def reenable(self) -> None:
            self.query_one(TabbedContent).get_tab("tab-2").disabled = False

    app = TabbedApp()
    async with app.run_test() as pilot:
        await pilot.click(f"Tab#{ContentTab.add_prefix('tab-2')}")
        assert app.query_one(TabbedContent).active == "tab-1"
        app.reenable()
        await pilot.click(f"Tab#{ContentTab.add_prefix('tab-2')}")
        assert app.query_one(TabbedContent).active == "tab-2"


async def test_reenabling_via_tabbed_content():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield Label("tab-1")
                yield Label("tab-2")

        def on_mount(self) -> None:
            self.query_one(TabbedContent).disable_tab("tab-2")

        def reenable(self) -> None:
            self.query_one(TabbedContent).enable_tab("tab-2")

    app = TabbedApp()
    async with app.run_test() as pilot:
        await pilot.click(f"Tab#{ContentTab.add_prefix('tab-2')}")
        assert app.query_one(TabbedContent).active == "tab-1"
        app.reenable()
        await pilot.click(f"Tab#{ContentTab.add_prefix('tab-2')}")
        assert app.query_one(TabbedContent).active == "tab-2"


async def test_reenabling_via_tab_pane():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield Label("tab-1")
                yield Label("tab-2")

        def on_mount(self) -> None:
            self.query_one("TabPane#tab-2").disabled = True

        def reenable(self) -> None:
            self.query_one("TabPane#tab-2").disabled = False

    app = TabbedApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.click(f"Tab#{ContentTab.add_prefix('tab-2')}")
        assert app.query_one(TabbedContent).active == "tab-1"
        app.reenable()
        await pilot.click(f"Tab#{ContentTab.add_prefix('tab-2')}")
        assert app.query_one(TabbedContent).active == "tab-2"


async def test_disabling_unknown_tab():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield Label("tab-1")

    app = TabbedApp()
    async with app.run_test():
        with pytest.raises(Tabs.TabError):
            app.query_one(TabbedContent).disable_tab("foo")


async def test_enabling_unknown_tab():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield Label("tab-1")

    app = TabbedApp()
    async with app.run_test():
        with pytest.raises(Tabs.TabError):
            app.query_one(TabbedContent).enable_tab("foo")


async def test_hide_unknown_tab():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield Label("tab-1")

    app = TabbedApp()
    async with app.run_test():
        with pytest.raises(Tabs.TabError):
            app.query_one(TabbedContent).hide_tab("foo")


async def test_show_unknown_tab():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield Label("tab-1")

    app = TabbedApp()
    async with app.run_test():
        with pytest.raises(Tabs.TabError):
            app.query_one(TabbedContent).show_tab("foo")


async def test_hide_show_messages():
    hide_msg = False
    show_msg = False

    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield Label("tab-1")

        def on_tabs_tab_hidden(self) -> None:
            nonlocal hide_msg
            hide_msg = True

        def on_tabs_tab_shown(self) -> None:
            nonlocal show_msg
            show_msg = True

    app = TabbedApp()
    async with app.run_test() as pilot:
        app.query_one(TabbedContent).hide_tab("tab-1")
        await pilot.pause()
        assert hide_msg
        app.query_one(TabbedContent).show_tab("tab-1")
        await pilot.pause()
        assert show_msg


async def test_hide_last_tab_means_no_tab_active():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield Label("tab-1")

    app = TabbedApp()
    async with app.run_test() as pilot:
        tabbed_content = app.query_one(TabbedContent)
        tabbed_content.hide_tab("tab-1")
        await pilot.pause()
        assert not tabbed_content.active


async def test_hiding_tabs_moves_active_to_next_tab():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield Label("tab-1")
                yield Label("tab-2")
                yield Label("tab-3")

    app = TabbedApp()
    async with app.run_test() as pilot:
        tabbed_content = app.query_one(TabbedContent)
        tabbed_content.hide_tab("tab-1")
        await pilot.pause()
        assert tabbed_content.active == "tab-2"
        tabbed_content.hide_tab("tab-2")
        await pilot.pause()
        assert tabbed_content.active == "tab-3"


async def test_showing_tabs_does_not_change_active_tab():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield Label("tab-1")
                yield Label("tab-2")
                yield Label("tab-3")

    app = TabbedApp()
    async with app.run_test() as pilot:
        tabbed_content = app.query_one(TabbedContent)
        tabbed_content.hide_tab("tab-1")
        tabbed_content.hide_tab("tab-2")
        await pilot.pause()
        # sanity check
        assert tabbed_content.active == "tab-3"

        tabbed_content.show_tab("tab-1")
        tabbed_content.show_tab("tab-2")
        assert tabbed_content.active == "tab-3"


@pytest.mark.parametrize("tab_id", ["tab-1", "tab-2"])
async def test_showing_first_tab_activates_tab(tab_id: str):
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield Label("tab-1")
                yield Label("tab-2")

    app = TabbedApp()
    async with app.run_test() as pilot:
        tabbed_content = app.query_one(TabbedContent)
        tabbed_content.hide_tab("tab-1")
        tabbed_content.hide_tab("tab-2")
        await pilot.pause()
        # sanity check
        assert not tabbed_content.active

        tabbed_content.show_tab(tab_id)
        await pilot.pause()
        assert tabbed_content.active == tab_id


async def test_disabling_nested_tabs():
    """Regression test for https://github.com/Textualize/textual/issues/3145."""

    class TabbedApp(App):
        def compose(self) -> ComposeResult:
            with TabbedContent(id="tabbed-content"):
                with TabPane("Tab Pane 1"):
                    yield Label("foo")
                with TabPane("Tab Pane 2"):
                    yield Label("bar")
                with TabPane("Tab Pane 3"):
                    with TabbedContent():
                        with TabPane("Inner Pane 1"):
                            yield Label("fizz")
                        with TabPane("Inner Pane 2"):
                            yield Label("bang")

    app = TabbedApp()
    async with app.run_test() as pilot:
        tabber = app.query_one("#tabbed-content", expect_type=TabbedContent)
        tabber.disable_tab("tab-1")
        await pilot.pause()
        tabber.enable_tab("tab-1")
        await pilot.pause()


async def test_hiding_nested_tabs():
    """Regression test for https://github.com/Textualize/textual/issues/3145."""

    class TabbedApp(App):
        def compose(self) -> ComposeResult:
            with TabbedContent(id="tabbed-content"):
                with TabPane("Tab Pane 1"):
                    yield Label("foo")
                with TabPane("Tab Pane 2"):
                    yield Label("bar")
                with TabPane("Tab Pane 3"):
                    with TabbedContent():
                        with TabPane("Inner Pane 1"):
                            yield Label("fizz")
                        with TabPane("Inner Pane 2"):
                            yield Label("bang")

    app = TabbedApp()
    async with app.run_test() as pilot:
        tabber = app.query_one("#tabbed-content", expect_type=TabbedContent)
        tabber.hide_tab("tab-1")
        await pilot.pause()
        tabber.show_tab("tab-1")
        await pilot.pause()


async def test_tabs_nested_in_tabbed_content_doesnt_crash():
    """Regression test for https://github.com/Textualize/textual/issues/3412"""

    class TabsNestedInTabbedContent(App):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                with TabPane("Outer TabPane"):
                    yield Tabs("Inner Tab")

    app = TabsNestedInTabbedContent()
    async with app.run_test() as pilot:
        await pilot.pause()


async def test_tabs_nested_doesnt_interfere_with_ancestor_tabbed_content():
    """When a Tabs is nested as a descendant in the DOM of a TabbedContent,
    the messages posted from that Tabs should not interfere with the TabbedContent.
    A TabbedContent should only handle messages from Tabs which are direct children.

    Relates to https://github.com/Textualize/textual/issues/3412
    """

    class TabsNestedInTabbedContent(App):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                with TabPane("OuterTab", id="outer1"):
                    yield Tabs(
                        Tab("Tab1", id="tab1"),
                        Tab("Tab2", id="tab2"),
                        id="inner-tabs",
                    )

    app = TabsNestedInTabbedContent()
    async with app.run_test():
        inner_tabs = app.query_one("#inner-tabs", Tabs)
        tabbed_content = app.query_one(TabbedContent)

        assert inner_tabs.active_tab.id == "tab1"
        assert tabbed_content.active == "outer1"

        await inner_tabs.clear()

        assert inner_tabs.active_tab is None
        assert tabbed_content.active == "outer1"


async def test_disabling_tab_within_tabbed_content_stays_isolated():
    """Disabling a tab within a tab pane should not affect the TabbedContent."""

    class TabsNestedInTabbedContent(App):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                with TabPane("TabbedContent", id="duplicate"):
                    yield Tabs(
                        Tab("Tab1", id="duplicate"),
                        Tab("Tab2", id="stay-enabled"),
                        id="test-tabs",
                    )

    app = TabsNestedInTabbedContent()
    async with app.run_test() as pilot:
        assert app.query_one("Tab#duplicate").disabled is False
        assert app.query_one("TabPane#duplicate").disabled is False
        app.query_one("#test-tabs", Tabs).disable("duplicate")
        await pilot.pause()
        assert app.query_one("Tab#duplicate").disabled is True
        assert app.query_one("TabPane#duplicate").disabled is False


async def test_tab_switch_with_focused_input():
    """Regression test for https://github.com/Textualize/textual/issues/4955.

    When a widget with focus (e.g. Input) is inside a TabbedContent,
    switching tabs via key binding should not re-activate the old tab.
    """

    class Bug4955App(App):
        BINDINGS = [
            ("ctrl+s", "switch_s", "S"),
            ("ctrl+t", "switch_t", "T"),
        ]

        def action_switch_s(self) -> None:
            self.query_one(TabbedContent).active = "s-tab"

        def action_switch_t(self) -> None:
            self.query_one(TabbedContent).active = "t-tab"

        def compose(self) -> ComposeResult:
            with TabbedContent(initial="s-tab"):
                with TabPane("S Group", id="s-tab"):
                    yield Input("sss", id="s-input")
                    yield Button("S", id="s-btn")
                with TabPane("T Group", id="t-tab"):
                    yield Input("ttt", id="t-input")
                    yield Button("T", id="t-btn")
            yield Footer()

    app = Bug4955App()
    async with app.run_test() as pilot:
        tabbed_content = app.query_one(TabbedContent)

        # Focus the input in the first tab
        app.query_one("#s-input", Input).focus()
        await pilot.pause()
        assert tabbed_content.active == "s-tab"

        # Switch to the second tab via key binding
        await pilot.press("ctrl+t")
        await pilot.pause()

        # The active tab should be "t-tab", not "s-tab"
        assert tabbed_content.active == "t-tab"
        assert tabbed_content.active_pane.id == "t-tab"


async def test_tab_switch_with_focused_input_via_click():
    """Switching tabs by clicking a tab while a widget has focus should work.

    Related to https://github.com/Textualize/textual/issues/4955.
    """

    class ClickSwitchApp(App):
        def compose(self) -> ComposeResult:
            with TabbedContent(initial="first"):
                with TabPane("First", id="first"):
                    yield Input("hello", id="first-input")
                with TabPane("Second", id="second"):
                    yield Input("world", id="second-input")

    app = ClickSwitchApp()
    async with app.run_test() as pilot:
        tabbed_content = app.query_one(TabbedContent)

        # Focus input in first tab
        app.query_one("#first-input", Input).focus()
        await pilot.pause()
        assert tabbed_content.active == "first"

        # Click the second tab
        await pilot.click(f"Tab#{ContentTab.add_prefix('second')}")
        await pilot.pause()

        # Should switch to second tab
        assert tabbed_content.active == "second"
        assert tabbed_content.active_pane.id == "second"


async def test_auto_tab_switch_on_programmatic_focus():
    """Programmatically focusing a widget in a hidden tab should auto-switch.

    Ensures the fix for #4955 doesn't break the auto-tab-switch feature.
    """

    class AutoSwitchApp(App):
        BINDINGS = [("space", "focus_btn2", "Focus btn2")]

        def action_focus_btn2(self) -> None:
            self.query_one("#btn-2", Button).focus()

        def compose(self) -> ComposeResult:
            with TabbedContent(initial="tab-1"):
                with TabPane("Tab 1", id="tab-1"):
                    yield Button("Button 1", id="btn-1")
                with TabPane("Tab 2", id="tab-2"):
                    yield Button("Button 2", id="btn-2")
            yield Footer()

    app = AutoSwitchApp()
    async with app.run_test() as pilot:
        tabbed_content = app.query_one(TabbedContent)
        assert tabbed_content.active == "tab-1"

        # Programmatically focus a widget in the hidden tab
        await pilot.press("space")
        await pilot.pause()

        # Auto-switch should activate tab-2
        assert tabbed_content.active == "tab-2"
        assert tabbed_content.active_pane.id == "tab-2"
