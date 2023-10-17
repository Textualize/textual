from __future__ import annotations

from asyncio import Future, gather, wait
from typing import Coroutine


class AwaitComplete:
    """An 'optionally-awaitable' object."""

    _instances: set["AwaitComplete"] = []
    """Track all active instances of AwaitComplete."""

    def __init__(self, *coroutine: Coroutine) -> None:
        """Create an AwaitComplete.

        Args:
            coroutine: One or more coroutines to execute.
        """
        self.coroutine = coroutine
        AwaitComplete._instances.add(self)
        self._future: Future = gather(*[coroutine for coroutine in self.coroutine])
        self._future.add_done_callback(self._on_done)

    async def __call__(self):
        await self

    def __await__(self):
        return self._future.__await__()

    def _on_done(self, _: Future) -> None:
        """Stop tracking this instance once it's done."""
        AwaitComplete._instances.remove(self)

    @property
    def is_done(self) -> bool:
        """Returns True if the task has completed."""
        return self._future is not None and self._future.done()

    @property
    def exception(self) -> BaseException | None:
        """An exception if it occurred in any of the coroutines."""
        if self._future and self._future.done():
            return self._future.exception()
        return None

    @classmethod
    async def wait_all(cls):
        """Await all instances of AwaitComplete."""
        await wait(
            [instance._future for instance in cls._instances if instance._future],
            timeout=1.0,
        )

    @classmethod
    def nothing(cls):
        """Returns an already completed instance of AwaitComplete."""
        instance = cls()
        instance._future = Future()
        instance._future.set_result(None)  # Mark it as completed with no result
        return instance
