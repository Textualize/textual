from __future__ import annotations

from asyncio import Future, gather, wait
from typing import Coroutine

from textual._asyncio import create_task


class AwaitComplete:
    """An 'optionally-awaitable' object.

    Supply a coroutine object, and it will run in
    a task which can either be awaited or called without awaiting in order
    to achieve 'fire-and-forget' behaviour.
    """

    _instances: list["AwaitComplete"] = []
    """Track all active instances of AwaitComplete."""

    def __init__(self, *coroutine: Coroutine) -> None:
        self.coroutine = coroutine
        self._future: Future | None = None
        AwaitComplete._instances.append(self)

    async def __call__(self):
        await self

    def __await__(self):
        if not self._future:
            self._future = gather(*self.coroutine)
            self._future.add_done_callback(self._on_done)
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
