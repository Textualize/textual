"""
Tests for scrolling animations, which are considered a basic animation.
(An animation that also plays on the level BASIC.)
"""

from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Label


class TallApp(App[None]):
    def compose(self) -> ComposeResult:
        with VerticalScroll():
            for _ in range(100):
                yield Label()


async def test_scrolling_animates_on_full() -> None:
    app = TallApp()
    app.animation_level = "full"

    async with app.run_test() as pilot:
        vertical_scroll = app.query_one(VerticalScroll)
        animator = app.animator
        # Freeze time at 0 before triggering the animation.
        animator._get_time = lambda *_: 0
        vertical_scroll.scroll_end(duration=10000)
        await pilot.pause()
        # Freeze time after the animation start and before animation end.
        animator._get_time = lambda *_: 0.01
        # Move to the next frame.
        animator()
        assert animator.is_being_animated(vertical_scroll, "scroll_y")


async def test_scrolling_animates_on_basic() -> None:
    app = TallApp()
    app.animation_level = "basic"

    async with app.run_test() as pilot:
        vertical_scroll = app.query_one(VerticalScroll)
        animator = app.animator
        # Freeze time at 0 before triggering the animation.
        animator._get_time = lambda *_: 0
        vertical_scroll.scroll_end(duration=10000)
        await pilot.pause()
        # Freeze time after the animation start and before animation end.
        animator._get_time = lambda *_: 0.01
        # Move to the next frame.
        animator()
        assert animator.is_being_animated(vertical_scroll, "scroll_y")


async def test_scrolling_does_not_animate_on_none() -> None:
    app = TallApp()
    app.animation_level = "none"

    async with app.run_test() as pilot:
        vertical_scroll = app.query_one(VerticalScroll)
        animator = app.animator
        # Freeze time at 0 before triggering the animation.
        animator._get_time = lambda *_: 0
        vertical_scroll.scroll_end(duration=10000)
        await pilot.pause()
        # Freeze time after the animation start and before animation end.
        animator._get_time = lambda *_: 0.01
        # Move to the next frame.
        animator()
        assert not animator.is_being_animated(vertical_scroll, "scroll_y")
