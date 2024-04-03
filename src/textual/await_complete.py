from __future__ import annotations

from asyncio import Future, gather
from typing import Any, Awaitable, Generator

import rich.repr


@rich.repr.auto(angular=True)
class AwaitComplete:
    """An 'optionally-awaitable' object which runs one or more coroutines (or other awaitables) concurrently."""

    def __init__(self, *awaitables: Awaitable) -> None:
        """Create an AwaitComplete.

        Args:
            awaitables: One or more awaitables to run concurrently.
        """
        self._future: Future[Any] = gather(*awaitables)

    async def __call__(self) -> Any:
        return await self

    def __await__(self) -> Generator[Any, None, Any]:
        return self._future.__await__()

    @property
    def is_done(self) -> bool:
        """`True` if the task has completed."""
        return self._future.done()

    @property
    def exception(self) -> BaseException | None:
        """An exception if the awaitables failed."""
        if self._future.done():
            return self._future.exception()
        return None

    @classmethod
    def nothing(cls):
        """Returns an already completed instance of AwaitComplete."""
        instance = cls()
        instance._future = Future()
        instance._future.set_result(None)  # Mark it as completed with no result
        return instance
