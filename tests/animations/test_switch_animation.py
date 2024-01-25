"""
Tests for the switch toggle animation, which is considered a basic animation.
(An animation that also plays on the level BASIC.)
"""

from textual.app import App, ComposeResult
from textual.constants import AnimationsEnum
from textual.widgets import Switch


class SwitchApp(App[None]):
    def compose(self) -> ComposeResult:
        yield Switch()


async def test_switch_animates_on_full() -> None:
    app = SwitchApp()
    app.show_animations = AnimationsEnum.FULL

    async with app.run_test():
        switch = app.query_one(Switch)
        switch.action_toggle()
        animator = app.animator
        # Move to the next animation frame.
        await animator()
        # The animation should still be running.
        assert app.animator.is_being_animated(switch, "slider_pos")


async def test_switch_animates_on_basic() -> None:
    app = SwitchApp()
    app.show_animations = AnimationsEnum.BASIC

    async with app.run_test():
        switch = app.query_one(Switch)
        switch.action_toggle()
        animator = app.animator
        # Move to the next animation frame.
        await animator()
        # The animation should still be running.
        assert app.animator.is_being_animated(switch, "slider_pos")


async def test_switch_does_not_animate_on_none() -> None:
    app = SwitchApp()
    app.show_animations = AnimationsEnum.NONE

    async with app.run_test():
        switch = app.query_one(Switch)
        switch.action_toggle()
        animator = app.animator
        # Let the animator handle pending animations.
        await animator()
        # The animation should be done.
        assert not app.animator.is_being_animated(switch, "slider_pos")
