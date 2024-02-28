"""
Tests for the tabs underline animation, which is considered a basic animation.
(An animation that also plays on the level BASIC.)
"""

from textual.app import App, ComposeResult
from textual.widgets import Label, TabbedContent, Tabs
from textual.widgets._tabs import Underline


class TabbedContentApp(App[None]):
    def compose(self) -> ComposeResult:
        with TabbedContent():
            for _ in range(10):
                yield Label("Hey!")


async def test_tabs_underline_animates_on_full() -> None:
    """The underline takes some time to move when animated."""
    app = TabbedContentApp()
    app.animation_level = "full"

    async with app.run_test() as pilot:
        underline = app.query_one(Underline)
        animator = app.animator
        # Freeze time at 0 before triggering the animation.
        animator._get_time = lambda *_: 0
        app.query_one(Tabs).action_previous_tab()
        await pilot.pause()
        # Freeze time after the animation start and before animation end.
        animator._get_time = lambda *_: 0.01
        # Move to the next frame.
        animator()
        assert animator.is_being_animated(underline, "highlight_start")
        assert animator.is_being_animated(underline, "highlight_end")


async def test_tabs_underline_animates_on_basic() -> None:
    """The underline takes some time to move when animated."""
    app = TabbedContentApp()
    app.animation_level = "basic"

    async with app.run_test() as pilot:
        underline = app.query_one(Underline)
        animator = app.animator
        # Freeze time at 0 before triggering the animation.
        animator._get_time = lambda *_: 0
        app.query_one(Tabs).action_previous_tab()
        await pilot.pause()
        # Freeze time after the animation start and before animation end.
        animator._get_time = lambda *_: 0.01
        # Move to the next frame.
        animator()
        assert animator.is_being_animated(underline, "highlight_start")
        assert animator.is_being_animated(underline, "highlight_end")


async def test_tabs_underline_does_not_animate_on_none() -> None:
    """The underline jumps to its final position when not animated."""
    app = TabbedContentApp()
    app.animation_level = "none"

    async with app.run_test() as pilot:
        underline = app.query_one(Underline)
        animator = app.animator
        # Freeze time at 0 before triggering the animation.
        animator._get_time = lambda *_: 0
        app.query_one(Tabs).action_previous_tab()
        await pilot.pause()
        # Freeze time after the animation start and before animation end.
        animator._get_time = lambda *_: 0.01
        # Move to the next frame.
        animator()
        assert not animator.is_being_animated(underline, "highlight_start")
        assert not animator.is_being_animated(underline, "highlight_end")
