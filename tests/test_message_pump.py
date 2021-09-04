import asyncio
import contextvars
import time

import pytest

from textual.message_pump import MessagePump


@pytest.mark.asyncio
async def test_execute_in_thread_parallelism():

    sleep_time = 0.1

    def blocking(*args, **kwargs) -> None:
        assert args == ("test_arg",)
        assert kwargs == {"kwarg": "expected"}
        time.sleep(sleep_time)

    pump = MessagePump()

    start = time.time()
    task = asyncio.create_task(
        pump.execute_in_thread(
            blocking, "test_arg", kwarg="expected"
        )
    )
    # if we didn't use execute_in_thread here,
    # calling sleep() would block the event loop
    # such that the background task would be paused
    # and total execution would take >= sleep_time * 2
    await pump.execute_in_thread(
        blocking, "test_arg", kwarg="expected"
    )
    await task
    end  = time.time()
    # test that both calls were made concurrently
    # this could be (end-start) <= sleep_time
    # but there is some overhead from creating tasks
    # creating the threadpool, etc.
    # such that we'd have to herusitcally determine a number
    # like (end-start) < sleep_time * 1.0123
    elapsed = end-start
    assert elapsed < sleep_time * 2, elapsed


@pytest.mark.asyncio
async def test_execute_in_thread_context():
    # Test that execute_in_thread carries any contextvars
    # into the thread that the blocking call is executed in

    ctxvar = contextvars.ContextVar("ctxvar")

    def in_thread_sync() -> int:
        return ctxvar.get()

    async def in_thread_async() -> int:
        return ctxvar.get()

    pump = MessagePump()
    ctxvar.set(1)

    assert (await pump.execute_in_thread(in_thread_sync)) == 1
    assert (await pump.execute_in_thread(in_thread_async)) == 1


@pytest.mark.asyncio
async def test_execute_in_thread_callable_class():
    # Test that execute_in_thread carries any contextvars
    # into the thread that the blocking call is executed in

    class TargetSync:

        def __call__(self) -> int:
            return 1
    
    class TargetAsync:
        async def __call__(self) -> int:
            return 1

    pump = MessagePump()

    assert (await pump.execute_in_thread(TargetAsync())) == 1
    assert (await pump.execute_in_thread(TargetSync())) == 1
