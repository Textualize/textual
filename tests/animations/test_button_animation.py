"""
Tests for the “button pressed” animation, which is considered a basic animation.
(An animation that also plays on the level BASIC.)
"""

from textual.app import App, ComposeResult
from textual.widgets import Button


class ButtonApp(App[None]):
    def compose(self) -> ComposeResult:
        yield Button()


async def test_button_animates_on_full() -> None:
    """The button click animation should play on FULL."""
    app = ButtonApp()
    app.animation_level = "full"

    async with app.run_test() as pilot:
        await pilot.click(Button)
        assert app.query_one(Button).has_class("-active")


async def test_button_animates_on_basic() -> None:
    """The button click animation should play on BASIC."""
    app = ButtonApp()
    app.animation_level = "basic"

    async with app.run_test() as pilot:
        await pilot.click(Button)
        assert app.query_one(Button).has_class("-active")


async def test_button_does_not_animate_on_none() -> None:
    """The button click animation should play on NONE."""
    app = ButtonApp()
    app.animation_level = "none"

    async with app.run_test() as pilot:
        await pilot.click(Button)
        assert not app.query_one(Button).has_class("-active")
