import asyncio
import time
import sys

import pytest

from textual._win_sleep import sleep
from textual.app import App

pytestmark = pytest.mark.skipif(
    sys.platform != "win32", reason="We only need to test this on Windows."
)


@pytest.mark.parametrize("sleep_for", [1, 10, 1000])
def test_win_sleep_timer_is_cancellable(sleep_for):
    """Regression test for https://github.com/Textualize/textual/issues/2711."""

    class WindowsIntervalBugApp(App[None]):
        def on_mount(self) -> None:
            self.set_interval(sleep_for, lambda: None)

        def key_e(self):
            self.exit()

    async def actual_test():
        async with WindowsIntervalBugApp().run_test() as pilot:
            await pilot.press("e")

    start = time.perf_counter()
    asyncio.run(actual_test())
    end = time.perf_counter()
    assert end - start < 0.1
