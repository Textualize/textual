from __future__ import annotations

from asyncio import Future, gather
from typing import Any, Coroutine, Iterator, TypeVar

import rich.repr

ReturnType = TypeVar("ReturnType")


@rich.repr.auto(angular=True)
class AwaitComplete:
    """An 'optionally-awaitable' object."""

    def __init__(self, *coroutines: Coroutine[Any, Any, Any]) -> None:
        """Create an AwaitComplete.

        Args:
            coroutines: One or more coroutines to execute.
        """
        self.coroutines: tuple[Coroutine[Any, Any, Any], ...] = coroutines
        self._future: Future = gather(*self.coroutines)

    async def __call__(self) -> Any:
        return await self

    def __await__(self) -> Iterator[None]:
        return self._future.__await__()

    @property
    def is_done(self) -> bool:
        """Returns True if the task has completed."""
        return self._future.done()

    @property
    def exception(self) -> BaseException | None:
        """An exception if it occurred in any of the coroutines."""
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
