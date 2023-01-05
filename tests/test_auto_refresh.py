import asyncio
import time
from typing import Tuple

from textual.app import App
from textual.pilot import Pilot


class RefreshApp(App[Tuple[float, float]]):
    def __init__(self) -> None:
        self.count = 0
        super().__init__()

    def on_mount(self) -> None:
        self.start_wall_clock = time.time()
        self.start_thread_clock = time.thread_time()
        self.auto_refresh = 0.1

    def _automatic_refresh(self) -> None:
        self.count += 1
        if self.count == 3:
            app_result = (
                time.time() - self.start_wall_clock,
                time.thread_time() - self.start_thread_clock,
            )
            self.exit(app_result)
        super()._automatic_refresh()


def test_auto_refresh() -> None:
    app = RefreshApp()

    async def quit_after(pilot: Pilot) -> None:
        await asyncio.sleep(1)

    app_result = app.run(auto_pilot=quit_after, headless=True)
    assert app_result is not None
    elapsed_wall_clock, elapsed_thread_clock = app_result

    # CI can run slower, so we need to give this a bit of margin
    # in terms of thread time this should take ~0.01s, but let's
    # give it 0.2s.
    assert 0.3 <= elapsed_wall_clock
    assert elapsed_thread_clock < 0.2
