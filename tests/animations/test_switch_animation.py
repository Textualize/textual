"""
Tests for the switch toggle animation, which is considered a basic animation.
(An animation that also plays on the level BASIC.)
"""

from textual.app import App, ComposeResult
from textual.widgets import Switch


class SwitchApp(App[None]):
    def compose(self) -> ComposeResult:
        yield Switch()


async def test_switch_animates_on_full() -> None:
    app = SwitchApp()
    app.animation_level = "full"

    async with app.run_test() as pilot:
        switch = app.query_one(Switch)
        animator = app.animator
        # Freeze time at 0 before triggering the animation.
        animator._get_time = lambda *_: 0
        switch.action_toggle_switch()
        await pilot.pause()
        # Freeze time after the animation start and before animation end.
        animator._get_time = lambda *_: 0.01
        # Move to the next frame.
        animator()
        # The animation should still be running.
        assert app.animator.is_being_animated(switch, "slider_pos")


async def test_switch_animates_on_basic() -> None:
    app = SwitchApp()
    app.animation_level = "basic"

    async with app.run_test() as pilot:
        switch = app.query_one(Switch)
        animator = app.animator
        # Freeze time at 0 before triggering the animation.
        animator._get_time = lambda *_: 0
        switch.action_toggle_switch()
        await pilot.pause()
        # Freeze time after the animation start and before animation end.
        animator._get_time = lambda *_: 0.01
        # Move to the next frame.
        animator()
        # The animation should still be running.
        assert app.animator.is_being_animated(switch, "slider_pos")


async def test_switch_does_not_animate_on_none() -> None:
    app = SwitchApp()
    app.animation_level = "none"

    async with app.run_test() as pilot:
        switch = app.query_one(Switch)
        animator = app.animator
        # Freeze time at 0 before triggering the animation.
        animator._get_time = lambda *_: 0
        switch.action_toggle_switch()
        await pilot.pause()
        # Freeze time after the animation start and before animation end.
        animator._get_time = lambda *_: 0.01
        # Move to the next frame.
        animator()
        # The animation should still be running.
        assert not app.animator.is_being_animated(switch, "slider_pos")
