import asyncio

import pytest

from textual.app import App
from textual.worker import (
    DeadlockError,
    NoActiveWorker,
    Worker,
    WorkerCancelled,
    WorkerError,
    WorkerFailed,
    WorkerState,
    get_current_worker,
)


async def test_initialize():
    """Test initial values."""

    def foo() -> str:
        return "foo"

    app = App()
    async with app.run_test():
        worker = Worker(app, foo, name="foo", group="foo-group", description="Foo test")
        repr(worker)

    assert worker.state == WorkerState.PENDING
    assert not worker.is_cancelled
    assert not worker.is_running
    assert not worker.is_finished
    assert worker.completed_steps == 0
    assert worker.total_steps is None
    assert worker.progress == 0.0
    assert worker.result is None


async def test_run_success() -> None:
    """Test successful runs."""

    def foo() -> str:
        """Regular function."""
        return "foo"

    async def bar() -> str:
        """Coroutine."""
        return "bar"

    async def baz() -> str:
        """Coroutine."""
        return "baz"

    class RunApp(App):
        pass

    app = RunApp()
    async with app.run_test():
        # Call regular function
        foo_worker: Worker[str] = Worker(
            app, foo, name="foo", group="foo-group", description="Foo test", thread=True
        )
        # Call coroutine function
        bar_worker: Worker[str] = Worker(
            app, bar, name="bar", group="bar-group", description="Bar test"
        )
        # Call coroutine
        baz_worker: Worker[str] = Worker(
            app, baz(), name="baz", group="baz-group", description="Baz test"
        )
        # Call coroutine function in a thread
        bar_thread_worker: Worker[str] = Worker(
            app, bar, name="bar", group="bar-group", description="Bar test", thread=True
        )
        # Call coroutine in a thread.
        baz_thread_worker: Worker[str] = Worker(
            app,
            baz(),
            name="baz",
            group="baz-group",
            description="Baz test",
            thread=True,
        )
        assert foo_worker.result is None
        assert bar_worker.result is None
        assert baz_worker.result is None
        assert bar_thread_worker.result is None
        assert baz_thread_worker.result is None
        foo_worker._start(app)
        bar_worker._start(app)
        baz_worker._start(app)
        bar_thread_worker._start(app)
        baz_thread_worker._start(app)
        assert await foo_worker.wait() == "foo"
        assert await bar_worker.wait() == "bar"
        assert await baz_worker.wait() == "baz"
        assert await bar_thread_worker.wait() == "bar"
        assert await baz_thread_worker.wait() == "baz"
        assert foo_worker.result == "foo"
        assert bar_worker.result == "bar"
        assert baz_worker.result == "baz"
        assert bar_thread_worker.result == "bar"
        assert baz_thread_worker.result == "baz"


async def test_run_error() -> None:
    async def run_error() -> str:
        await asyncio.sleep(0.1)
        1 / 0
        return "Never"

    class ErrorApp(App):
        pass

    app = ErrorApp()
    with pytest.raises(WorkerFailed):
        async with app.run_test():
            worker: Worker[str] = Worker(app, run_error)
            worker._start(app)
            await worker.wait()


async def test_run_cancel() -> None:
    """Test run may be cancelled."""

    async def run_error() -> str:
        await asyncio.sleep(0.1)
        return "Never"

    class ErrorApp(App):
        pass

    app = ErrorApp()
    async with app.run_test():
        worker: Worker[str] = Worker(app, run_error)
        worker._start(app)
        await asyncio.sleep(0)
        worker.cancel()
        assert worker.is_cancelled
        with pytest.raises(WorkerCancelled):
            await worker.wait()


async def test_run_cancel_immediately() -> None:
    """Edge case for cancelling immediately."""

    async def run_error() -> str:
        await asyncio.sleep(0.1)
        return "Never"

    class ErrorApp(App):
        pass

    app = ErrorApp()
    async with app.run_test():
        worker: Worker[str] = Worker(app, run_error)
        worker._start(app)
        worker.cancel()
        assert worker.is_cancelled
        with pytest.raises(WorkerCancelled):
            await worker.wait()


async def test_get_worker() -> None:
    """Check get current worker."""

    async def run_worker() -> Worker:
        worker = get_current_worker()
        return worker

    class WorkerApp(App):
        pass

    app = WorkerApp()
    async with app.run_test():
        worker: Worker[Worker] = Worker(app, run_worker)
        worker._start(app)

        assert await worker.wait() is worker


def test_no_active_worker() -> None:
    """No active worker raises a specific exception."""
    with pytest.raises(NoActiveWorker):
        get_current_worker()


async def test_progress_update():
    async def long_work():
        pass

    app = App()
    async with app.run_test():
        worker = Worker(app, long_work)
        worker._start(app)
        worker.update(total_steps=100)
        assert worker.progress == 0
        worker.advance(50)
        assert worker.progress == 50
        worker.update(completed_steps=23)
        assert worker.progress == 73


async def test_double_start():
    async def long_work():
        return 0

    app = App()
    async with app.run_test():
        worker = Worker(app, long_work)
        worker._start(app)
        worker._start(app)
        assert await worker.wait() == 0


async def test_self_referential_deadlock():
    async def self_referential_work():
        await get_current_worker().wait()

    app = App()
    with pytest.raises(WorkerFailed) as exc:
        async with app.run_test():
            worker = Worker(app, self_referential_work)
            worker._start(app)
            await worker.wait()
        assert exc.type is DeadlockError


async def test_wait_without_start():
    async def work():
        return

    app = App()
    async with app.run_test():
        worker = Worker(app, work)
        with pytest.raises(WorkerError):
            await worker.wait()
