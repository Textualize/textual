"""
Tests for the loading indicator animation, which is considered a basic animation.
(An animation that also plays on the level BASIC.)
"""

from textual.app import App
from textual.constants import AnimationsEnum
from textual.widgets import LoadingIndicator


async def test_loading_indicator_is_not_static_on_full() -> None:
    """The loading indicator doesn't fall back to the static render on FULL."""
    app = App()
    app.show_animations = AnimationsEnum.FULL

    async with app.run_test() as pilot:
        app.screen.loading = True
        await pilot.pause()
        indicator = app.query_one(LoadingIndicator)
        assert str(indicator.render()) != "Loading..."


async def test_loading_indicator_is_not_static_on_basic() -> None:
    """The loading indicator doesn't fall back to the static render on BASIC."""
    app = App()
    app.show_animations = AnimationsEnum.BASIC

    async with app.run_test() as pilot:
        app.screen.loading = True
        await pilot.pause()
        indicator = app.query_one(LoadingIndicator)
        assert str(indicator.render()) != "Loading..."


async def test_loading_indicator_is_static_on_none() -> None:
    """The loading indicator falls back to the static render on NONE."""
    app = App()
    app.show_animations = AnimationsEnum.NONE

    async with app.run_test() as pilot:
        app.screen.loading = True
        await pilot.pause()
        indicator = app.query_one(LoadingIndicator)
        assert str(indicator.render()) == "Loading..."
