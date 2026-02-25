"""Regression test for https://github.com/Textualize/textual/issues/6370

A timer with interval=0 should not raise ZeroDivisionError.
"""

from textual.app import App


class ZeroIntervalApp(App[None]):
    """App that creates a timer with zero interval."""

    timer_fired = False

    def on_mount(self) -> None:
        self.set_interval(0, self._on_timer, repeat=3)

    def _on_timer(self) -> None:
        ZeroIntervalApp.timer_fired = True


async def test_zero_interval_timer_no_crash():
    """A timer with interval=0 should not raise ZeroDivisionError."""
    async with ZeroIntervalApp().run_test() as pilot:
        await pilot.pause()
        await pilot.pause()
        # The test passes if we get here without ZeroDivisionError
        assert ZeroIntervalApp.timer_fired
