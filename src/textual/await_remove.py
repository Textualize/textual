from asyncio import Event
from typing import Generator


class AwaitRemove:
    def __init__(self, finished_flag: Event) -> None:
        self.finished_flag = finished_flag

    def __await__(self) -> Generator[None, None, None]:
        async def await_prune() -> None:
            await self.finished_flag.wait()

        return await_prune().__await__()
