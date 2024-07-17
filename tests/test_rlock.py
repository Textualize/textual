import asyncio

import pytest

from textual.rlock import RLock


async def test_simple_lock():
    lock = RLock()
    # Starts not locked
    assert not lock.is_locked
    # Acquire the lock
    await lock.acquire()
    assert lock.is_locked
    # Acquire a second time (should not block)
    await lock.acquire()
    assert lock.is_locked

    # Release the lock
    lock.release()
    # Should still be locked
    assert lock.is_locked
    # Release the lock
    lock.release()
    # Should be released
    assert not lock.is_locked

    # Another release is a runtime error
    with pytest.raises(RuntimeError):
        lock.release()


async def test_multiple_tasks() -> None:
    """Check RLock prevents other tasks from acquiring lock."""
    lock = RLock()

    started: list[int] = []
    done: list[int] = []

    async def test_task(n: int) -> None:
        started.append(n)
        async with lock:
            done.append(n)

    async with lock:
        assert done == []
        task1 = asyncio.create_task(test_task(1))
        assert sorted(started) == []
        task2 = asyncio.create_task(test_task(2))
        await asyncio.sleep(0)
        assert sorted(started) == [1, 2]

    await task1
    assert 1 in done
    await task2
    assert 2 in done
