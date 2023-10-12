from asyncio import Event, Task
from typing import Awaitable, Generator


class AwaitComplete:
    """An optionally awaitable object that may be awaited to ensure completion of a coroutine."""

    def __init__(self, awaitable: Awaitable) -> None:
        """Initialise the instance of `AwaitComplete`.

        Args:
            awaitable: An awaitable to (optionally) await completion of.
        """
        self._awaitable = awaitable

    async def __call__(self) -> None:
        # TODO: Look at how AwaitRemove etc use call_next/call_later here.
        #  if we dont await things, then we can use these methods to put them
        #  on to a messagepump and ensure they complete.
        await self

    def __await__(self) -> Generator[None, None, None]:
        return self._awaitable.__await__()
