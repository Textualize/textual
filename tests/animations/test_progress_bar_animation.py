"""
Tests for the indeterminate progress bar animation, which is considered a basic
animation. (An animation that also plays on the level BASIC.)
"""

from textual.app import App, ComposeResult
from textual.widgets import ProgressBar
from textual.widgets._progress_bar import Bar


class ProgressBarApp(App[None]):
    def compose(self) -> ComposeResult:
        yield ProgressBar()


async def test_progress_bar_animates_on_full() -> None:
    """An indeterminate progress bar is not fully highlighted when animating."""
    app = ProgressBarApp()
    app.animation_level = "full"

    async with app.run_test():
        bar_renderable = app.query_one(Bar).render()
        start, end = bar_renderable.highlight_range
        assert start != 0 or end != app.query_one(Bar).size.width


async def test_progress_bar_animates_on_basic() -> None:
    """An indeterminate progress bar is not fully highlighted when animating."""
    app = ProgressBarApp()
    app.animation_level = "basic"

    async with app.run_test():
        bar_renderable = app.query_one(Bar).render()
        start, end = bar_renderable.highlight_range
        assert start != 0 or end != app.query_one(Bar).size.width


async def test_progress_bar_does_not_animate_on_none() -> None:
    """An indeterminate progress bar is fully highlighted when not animating."""
    app = ProgressBarApp()
    app.animation_level = "none"

    async with app.run_test():
        bar_renderable = app.query_one(Bar).render()
        start, end = bar_renderable.highlight_range
        assert start == 0
        assert end == app.query_one(Bar).size.width
