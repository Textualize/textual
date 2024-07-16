from __future__ import annotations

from asyncio import Lock, Task, current_task


class RLock:
    """A re-entrant asyncio lock."""

    def __init__(self) -> None:
        self._owner: Task | None = None
        self._count = 0
        self._lock = Lock()

    async def acquire(self) -> None:
        """Wait until the lock can be acquired."""
        task = current_task()
        assert task is not None
        if self._owner is None or self._owner is not task:
            await self._lock.acquire()
            self._owner = task
        self._count += 1

    def release(self) -> None:
        """Release a previously acquired lock."""
        task = current_task()
        assert task is not None
        self._count -= 1
        if self._count < 0:
            # Should not occur if every acquire as a release
            raise RuntimeError("RLock.release called too many times")
        if self._owner is task:
            if not self._count:
                self._owner = None
                self._lock.release()

    @property
    def is_locked(self):
        """Return True if lock is acquired."""
        return self._lock.locked()

    async def __aenter__(self) -> None:
        """Asynchronous context manager to acquire and release lock."""
        await self.acquire()

    async def __aexit__(self, _type, _value, _traceback) -> None:
        """Exit the context manager."""
        self.release()


if __name__ == "__main__":
    from asyncio import Lock

    async def locks():
        lock = RLock()
        async with lock:
            async with lock:
                print("Hello")

    import asyncio

    asyncio.run(locks())
