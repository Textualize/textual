"""
Tests for the loading indicator animation, which is considered a basic animation.
(An animation that also plays on the level BASIC.)
"""

from textual.app import App


async def test_loading_indicator_is_not_static_on_full() -> None:
    """The loading indicator doesn't fall back to the static render on FULL."""
    app = App()
    app.animation_level = "full"

    async with app.run_test() as pilot:
        app.screen.loading = True
        await pilot.pause()
        indicator = app.screen._cover_widget
        assert str(indicator.render()) != "Loading..."


async def test_loading_indicator_is_not_static_on_basic() -> None:
    """The loading indicator doesn't fall back to the static render on BASIC."""
    app = App()
    app.animation_level = "basic"

    async with app.run_test() as pilot:
        app.screen.loading = True
        await pilot.pause()
        indicator = app.screen._cover_widget
        assert str(indicator.render()) != "Loading..."


async def test_loading_indicator_is_static_on_none() -> None:
    """The loading indicator falls back to the static render on NONE."""
    app = App()
    app.animation_level = "none"

    async with app.run_test() as pilot:
        app.screen.loading = True
        await pilot.pause()
        indicator = app.screen._cover_widget
        assert str(indicator.render()) == "Loading..."
