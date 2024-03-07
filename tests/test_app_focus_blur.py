"""Test the workings of reacting to AppFocus and AppBlur."""

from textual.app import App, ComposeResult
from textual.events import AppBlur, AppFocus
from textual.widgets import Input


class FocusBlurApp(App[None]):

    AUTO_FOCUS = "#input-4"

    def compose(self) -> ComposeResult:
        for n in range(10):
            yield Input(id=f"input-{n}")


async def test_app_blur() -> None:
    """Test that AppBlur removes focus."""
    async with FocusBlurApp().run_test() as pilot:
        assert pilot.app.focused is not None
        assert pilot.app.focused.id == "input-4"
        pilot.app.post_message(AppBlur())
        await pilot.pause()
        assert pilot.app.focused is None


async def test_app_focus_restores_focus() -> None:
    """Test that AppFocus restores the correct focus."""
    async with FocusBlurApp().run_test() as pilot:
        assert pilot.app.focused is not None
        assert pilot.app.focused.id == "input-4"
        pilot.app.post_message(AppBlur())
        await pilot.pause()
        assert pilot.app.focused is None
        pilot.app.post_message(AppFocus())
        await pilot.pause()
        assert pilot.app.focused is not None
        assert pilot.app.focused.id == "input-4"


async def test_app_focus_restores_none_focus() -> None:
    """Test that AppFocus doesn't set focus if nothing was focused."""
    async with FocusBlurApp().run_test() as pilot:
        pilot.app.screen.focused = None
        pilot.app.post_message(AppBlur())
        await pilot.pause()
        assert pilot.app.focused is None
        pilot.app.post_message(AppFocus())
        await pilot.pause()
        assert pilot.app.focused is None


async def test_app_focus_handles_missing_widget() -> None:
    """Test that AppFocus works even when the last-focused widget has gone away."""
    async with FocusBlurApp().run_test() as pilot:
        assert pilot.app.focused is not None
        assert pilot.app.focused.id == "input-4"
        pilot.app.post_message(AppBlur())
        await pilot.pause()
        assert pilot.app.focused is None
        await pilot.app.query_one("#input-4").remove()
        pilot.app.post_message(AppFocus())
        await pilot.pause()
        assert pilot.app.focused is None


async def test_app_focus_defers_to_new_focus() -> None:
    """Test that AppFocus doesn't undo a fresh focus done while the app is in AppBlur state."""
    async with FocusBlurApp().run_test() as pilot:
        assert pilot.app.focused is not None
        assert pilot.app.focused.id == "input-4"
        pilot.app.post_message(AppBlur())
        await pilot.pause()
        assert pilot.app.focused is None
        pilot.app.query_one("#input-1").focus()
        await pilot.pause()
        pilot.app.post_message(AppFocus())
        await pilot.pause()
        assert pilot.app.focused.id == "input-1"
