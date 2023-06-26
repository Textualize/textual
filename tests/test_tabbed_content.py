import pytest

from textual.app import App, ComposeResult
from textual.reactive import var
from textual.widgets import Label, Tab, TabbedContent, TabPane, Tabs


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
        await pilot.pause()
        assert app.query_one("#foo-label").region
        assert not app.query_one("#bar-label").region
        assert not app.query_one("#baz-label").region

        # Click second tab
        await pilot.click("Tab#bar")
        assert tabbed_content.active == "bar"
        await pilot.pause()
        assert not app.query_one("#foo-label").region
        assert app.query_one("#bar-label").region
        assert not app.query_one("#baz-label").region

        # Click third tab
        await pilot.click("Tab#baz")
        assert tabbed_content.active == "baz"
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

        # Check fail with empty tab
        with pytest.raises(ValueError):
            tabbed_content.active = ""


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
        message = None

        def compose(self) -> ComposeResult:
            with TabbedContent(initial="bar"):
                with TabPane("foo", id="foo"):
                    yield Label("Foo", id="foo-label")

                with TabPane("bar", id="bar"):
                    yield Label("Bar", id="bar-label")
                with TabPane("baz", id="baz"):
                    yield Label("Baz", id="baz-label")

        def on_tabbed_content_tab_activated(
            self, event: TabbedContent.TabActivated
        ) -> None:
            self.message = event

    app = TabbedApp()
    async with app.run_test() as pilot:
        tabbed_content = app.query_one(TabbedContent)
        tabbed_content.active = "bar"
        await pilot.pause()
        assert isinstance(app.message, TabbedContent.TabActivated)
        assert app.message.tab.label.plain == "bar"


async def test_tabbed_content_add_later_from_empty():
    class TabbedApp(App[None]):
        def compose(self) -> ComposeResult:
            yield TabbedContent()

    async with TabbedApp().run_test() as pilot:
        tabbed_content = pilot.app.query_one(TabbedContent)
        assert tabbed_content.active == ""
        assert tabbed_content.tab_count == 0
        await tabbed_content.add_pane(TabPane("Test 1", id="test-1"))
        await pilot.pause()
        assert tabbed_content.tab_count == 1
        assert tabbed_content.active == "test-1"
        await tabbed_content.add_pane(TabPane("Test 2", id="test-2"))
        await pilot.pause()
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
        await pilot.pause()
        assert tabbed_content.tab_count == 4
        assert tabbed_content.active == "initial-1"
        await tabbed_content.add_pane(TabPane("Test 5", id="test-2"))
        await pilot.pause()
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
        await pilot.pause()
        assert tabbed_content.tab_count == 2
        assert tabbed_content.active == "initial-1"
        assert [tab.id for tab in tabbed_content.query(Tab).results(Tab)] == [
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
        await pilot.pause()
        assert tabbed_content.tab_count == 2
        assert tabbed_content.active == "initial-1"
        assert [tab.id for tab in tabbed_content.query(Tab).results(Tab)] == [
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
        await pilot.pause()
        assert tabbed_content.tab_count == 2
        assert tabbed_content.active == "initial-1"
        assert [tab.id for tab in tabbed_content.query(Tab).results(Tab)] == [
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
        assert [tab.id for tab in tabbed_content.query(Tab).results(Tab)] == [
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
