from textual.app import App
from textual.worker import Worker, WorkerState


def test_initialize():
    """Test initial values."""

    def foo() -> str:
        return "foo"

    worker = Worker(foo, name="foo", group="foo-group", description="Foo test")
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
            foo, name="foo", group="foo-group", description="Foo test"
        )
        # Call coroutine function
        bar_worker: Worker[str] = Worker(
            bar, name="bar", group="bar-group", description="Bar test"
        )
        # Call coroutine
        baz_worker: Worker[str] = Worker(
            baz(), name="baz", group="baz-group", description="Baz test"
        )
        assert foo_worker.result is None
        assert bar_worker.result is None
        assert baz_worker.result is None
        foo_worker._start(app)
        bar_worker._start(app)
        baz_worker._start(app)
        assert await foo_worker.wait() == "foo"
        assert await bar_worker.wait() == "bar"
        assert await baz_worker.wait() == "baz"
        assert foo_worker.result == "foo"
        assert bar_worker.result == "bar"
        assert baz_worker.result == "baz"
