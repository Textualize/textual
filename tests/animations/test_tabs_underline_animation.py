"""
Tests for the tabs underline animation, which is considered a basic animation.
(An animation that also plays on the level BASIC.)
"""

from textual.app import App, ComposeResult
from textual.constants import AnimationsEnum
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
    app.show_animations = AnimationsEnum.FULL

    async with app.run_test():
        underline = app.query_one(Underline)
        before = underline._highlight_range
        app.query_one(Tabs).action_previous_tab()
        assert before == underline._highlight_range


async def test_tabs_underline_animates_on_basic() -> None:
    """The underline takes some time to move when animated."""
    app = TabbedContentApp()
    app.show_animations = AnimationsEnum.BASIC

    async with app.run_test():
        underline = app.query_one(Underline)
        before = underline._highlight_range
        app.query_one(Tabs).action_previous_tab()
        assert before == underline._highlight_range


async def test_tabs_underline_does_not_animate_on_none() -> None:
    """The underline jumps to its final position when not animated."""
    app = TabbedContentApp()
    app.show_animations = AnimationsEnum.NONE

    async with app.run_test():
        underline = app.query_one(Underline)
        before = underline._highlight_range
        app.query_one(Tabs).action_previous_tab()
        assert before != underline._highlight_range
