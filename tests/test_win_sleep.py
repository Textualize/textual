from functools import partial
import time
import sys

import pytest

from textual._win_sleep import sleep
from textual.app import App

pytestmark = pytest.mark.skipif(
    sys.platform != "win32", reason="We only need to test this on Windows."
)


@pytest.mark.parametrize("sleep_for", [0.1, 1, 10])
async def test_win_sleep_duration(sleep_for):
    start = time.perf_counter()
    await sleep(sleep_for)
    end = time.perf_counter()
    assert end - start == pytest.approx(sleep_for, abs=min(sleep_for, 0.1))
    assert (end - start) < min(sleep_for, 0.1) + sleep_for
    assert end - start


@pytest.mark.parametrize("sleep_for", [0.1, 1, 10])
async def test_win_sleep_timer_is_cancellable(sleep_for):
    """Regression test for https://github.com/Textualize/textual/issues/2711."""

    class WindowsIntervalBugApp(App[None]):
        def on_mount(self) -> None:
            self.set_interval(sleep_for, lambda: None)

        def key_e(self):
            self.exit()

    async with WindowsIntervalBugApp().run_test() as pilot:
        start = time.perf_counter()
        await pilot.press("e")
        end = time.perf_counter()

    assert (end - start) < 0.05
