"""
Tests for the tabs underline animation, which is considered a basic animation.
(An animation that also plays on the level BASIC.)
"""

from textual.app import App, ComposeResult
from textual.widgets import Label, TabbedContent, Tabs


class TabbedContentApp(App[None]):
    def compose(self) -> ComposeResult:
        with TabbedContent():
            for _ in range(10):
                yield Label("Hey!")


async def test_tabs_underline_animates_on_full() -> None:
    """The underline takes some time to move when animated."""
    app = TabbedContentApp()
    app.animation_level = "full"

    animations: list[str] = []

    async with app.run_test() as pilot:
        animator = app.animator
        animator._record_animation = animations.append
        app.query_one(Tabs).action_previous_tab()
        await pilot.pause()
        assert "highlight_start" in animations
        assert "highlight_end" in animations


async def test_tabs_underline_animates_on_basic() -> None:
    """The underline takes some time to move when animated."""
    app = TabbedContentApp()
    app.animation_level = "basic"

    animations: list[str] = []

    async with app.run_test() as pilot:
        animator = app.animator
        animator._record_animation = animations.append
        app.query_one(Tabs).action_previous_tab()
        await pilot.pause()
        assert "highlight_start" in animations
        assert "highlight_end" in animations


async def test_tabs_underline_does_not_animate_on_none() -> None:
    """The underline jumps to its final position when not animated."""
    app = TabbedContentApp()
    app.animation_level = "none"

    animations: list[str] = []

    async with app.run_test() as pilot:
        animator = app.animator
        animator._record_animation = animations.append
        app.query_one(Tabs).action_previous_tab()
        await pilot.pause()
        assert "highlight_start" not in animations
        assert "highlight_end" not in animations
