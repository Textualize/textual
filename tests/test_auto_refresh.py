import asyncio
from time import time

from textual.app import App
from textual.pilot import Pilot


class RefreshApp(App[float]):
    def __init__(self):
        self.count = 0
        super().__init__()

    def on_mount(self):
        self.start = time()
        self.auto_refresh = 0.1

    def automatic_refresh(self):
        self.count += 1
        if self.count == 3:
            self.exit(time() - self.start)
        super().automatic_refresh()


def test_auto_refresh():
    app = RefreshApp()

    async def quit_after(pilot: Pilot) -> None:
        await asyncio.sleep(1)

    elapsed = app.run(auto_pilot=quit_after, headless=True)
    assert elapsed is not None
    # CI can run slower, so we need to give this a bit of margin
    assert 0.2 <= elapsed < 0.8
