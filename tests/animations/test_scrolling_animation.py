"""
Tests for scrolling animations, which are considered a basic animation.
(An animation that also plays on the level BASIC.)
"""

from textual.app import App, ComposeResult
from textual.constants import AnimationsEnum
from textual.containers import VerticalScroll
from textual.widgets import Label


class TallApp(App[None]):
    def compose(self) -> ComposeResult:
        with VerticalScroll():
            for _ in range(100):
                yield Label()


async def test_scrolling_animates_on_full() -> None:
    app = TallApp()
    app.show_animations = AnimationsEnum.FULL

    async with app.run_test() as pilot:
        vertical_scroll = app.query_one(VerticalScroll)
        current_scroll = vertical_scroll.scroll_offset
        # A ridiculously long duration means that in the fraction of a second
        # we take to check the scroll position again we haven't moved yet.
        vertical_scroll.scroll_end(duration=10000)
        await pilot.pause()
        assert vertical_scroll.scroll_offset == current_scroll


async def test_scrolling_animates_on_basic() -> None:
    app = TallApp()
    app.show_animations = AnimationsEnum.BASIC

    async with app.run_test() as pilot:
        vertical_scroll = app.query_one(VerticalScroll)
        current_scroll = vertical_scroll.scroll_offset
        # A ridiculously long duration means that in the fraction of a second
        # we take to check the scroll position again we haven't moved yet.
        vertical_scroll.scroll_end(duration=10000)
        await pilot.pause()
        assert vertical_scroll.scroll_offset == current_scroll


async def test_scrolling_does_not_animate_on_none() -> None:
    app = TallApp()
    app.show_animations = AnimationsEnum.NONE

    async with app.run_test() as pilot:
        vertical_scroll = app.query_one(VerticalScroll)
        current_scroll = vertical_scroll.scroll_offset
        # Even with a supposedly really long scroll animation duration,
        # we jump to the end because we're not animating.
        vertical_scroll.scroll_end(duration=10000)
        await pilot.pause()
        assert vertical_scroll.scroll_offset != current_scroll
