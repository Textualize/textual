from __future__ import annotations

from asyncio import Future, get_running_loop
from threading import Event, Thread
from time import perf_counter, sleep


class Sleeper(Thread):
    def __init__(
        self,
    ) -> None:
        self._exit = False
        self._sleep_time = 0.0
        self._event = Event()
        self.future: Future | None = None
        self._loop = get_running_loop()
        super().__init__(daemon=True)

    def run(self):
        while True:
            self._event.wait()
            if self._exit:
                break
            sleep(self._sleep_time)
            self._event.clear()
            # self.future.set_result(None)
            assert self.future is not None
            self._loop.call_soon_threadsafe(self.future.set_result, None)

    async def sleep(self, sleep_time: float) -> None:
        future = self.future = self._loop.create_future()
        self._sleep_time = sleep_time
        self._event.set()
        await future


async def check_sleeps() -> None:
    sleeper = Sleeper()
    sleeper.start()

    async def profile_sleep(sleep_for: float) -> float:
        start = perf_counter()

        while perf_counter() - start < sleep_for:
            sleep(0)
        elapsed = perf_counter() - start
        return elapsed

    for t in range(15, 120, 5):
        sleep_time = 1 / t
        elapsed = await profile_sleep(sleep_time)
        difference = (elapsed / sleep_time * 100) - 100
        print(
            f"sleep={sleep_time*1000:.01f}ms clock={elapsed*1000:.01f}ms diff={difference:.02f}%"
        )


from asyncio import run

run(check_sleeps())
