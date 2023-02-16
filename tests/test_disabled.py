"""Test Widget.disabled."""

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import (
    Button,
    DataTable,
    DirectoryTree,
    Input,
    ListView,
    Markdown,
    MarkdownViewer,
    Switch,
    TextLog,
    Tree,
)


class DisableApp(App[None]):
    """Application for testing Widget.disabled."""

    def compose(self) -> ComposeResult:
        """Compose the child widgets."""
        yield Vertical(
            Button(),
            DataTable(),
            DirectoryTree("."),
            Input(),
            ListView(),
            Switch(),
            TextLog(),
            Tree("Test"),
            Markdown(),
            MarkdownViewer(),
            id="test-container",
        )


async def test_all_initially_enabled() -> None:
    """All widgets should start out enabled."""
    async with DisableApp().run_test() as pilot:
        assert all(
            not node.disabled for node in pilot.app.screen.query("#test-container > *")
        )


async def test_enabled_widgets_have_enabled_pseudo_class() -> None:
    """All enabled widgets should have the :enabled pseudoclass."""
    async with DisableApp().run_test() as pilot:
        assert all(
            node.has_pseudo_class("enabled") and not node.has_pseudo_class("disabled")
            for node in pilot.app.screen.query("#test-container > *")
        )


async def test_all_individually_disabled() -> None:
    """Post-disable all widgets should report being disabled."""
    async with DisableApp().run_test() as pilot:
        for node in pilot.app.screen.query("Vertical > *"):
            node.disabled = True
        assert all(
            node.disabled for node in pilot.app.screen.query("#test-container > *")
        )


async def test_disabled_widgets_have_disabled_pseudo_class() -> None:
    """All disabled widgets should have the :disabled pseudoclass."""
    async with DisableApp().run_test() as pilot:
        for node in pilot.app.screen.query("#test-container > *"):
            node.disabled = True
        assert all(
            node.has_pseudo_class("disabled") and not node.has_pseudo_class("enabled")
            for node in pilot.app.screen.query("#test-container > *")
        )


async def test_disable_via_container() -> None:
    """All child widgets should appear (to CSS) as disabled by a container being disabled."""
    async with DisableApp().run_test() as pilot:
        pilot.app.screen.query_one("#test-container", Vertical).disabled = True
        assert all(
            node.has_pseudo_class("disabled") and not node.has_pseudo_class("enabled")
            for node in pilot.app.screen.query("#test-container > *")
        )
