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

    async with app.run_test() as pilot:
        switch = app.query_one(Switch)
        before = switch.slider_pos
        switch.action_toggle()
        await pilot.pause()
        assert abs(switch.slider_pos - before) < 1


async def test_switch_animates_on_basic() -> None:
    app = SwitchApp()
    app.show_animations = AnimationsEnum.BASIC

    async with app.run_test() as pilot:
        switch = app.query_one(Switch)
        before = switch.slider_pos
        switch.action_toggle()
        await pilot.pause()
        assert abs(switch.slider_pos - before) < 1


async def test_switch_does_not_animate_on_none() -> None:
    app = SwitchApp()
    app.show_animations = AnimationsEnum.NONE

    async with app.run_test() as pilot:
        switch = app.query_one(Switch)
        before = switch.slider_pos
        switch.action_toggle()
        await pilot.pause()
        assert abs(switch.slider_pos - before) == 1
