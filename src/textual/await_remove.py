"""Provides the type of an awaitable remove."""

from asyncio import Event
from typing import Generator


class AwaitRemove:
    """An awaitable returned by App.remove and DOMQuery.remove."""

    def __init__(self, finished_flag: Event) -> None:
        """Initialise the instance of ``AwaitRemove``.

        Args:
            finished_flag (asyncio.Event): The asyncio event to wait on.
        """
        self.finished_flag = finished_flag

    def __await__(self) -> Generator[None, None, None]:
        async def await_prune() -> None:
            """Wait for the prune operation to finish."""
            await self.finished_flag.wait()

        return await_prune().__await__()
