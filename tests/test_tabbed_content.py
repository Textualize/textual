import pytest

from textual.app import App, ComposeResult
from textual.widgets import Label, TabbedContent, TabPane


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
