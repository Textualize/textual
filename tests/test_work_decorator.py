import asyncio

import pytest

from textual import work
from textual._work_decorator import WorkerDeclarationError
from textual.app import App
from textual.worker import Worker, WorkerState


async def test_work() -> None:
    """Test basic usage of the @work decorator."""
    states: list[WorkerState] = []

    class WorkApp(App):
        worker: Worker

        @work
        async def foo(self) -> str:
            await asyncio.sleep(0.1)
            return "foo"

        def on_mount(self) -> None:
            self.worker = self.foo()

        def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
            states.append(event.state)

    app = WorkApp()

    async with app.run_test() as pilot:
        await app.workers.wait_for_complete()
        result = await app.worker.wait()
        assert result == "foo"
        await pilot.pause()
    assert states == [WorkerState.PENDING, WorkerState.RUNNING, WorkerState.SUCCESS]


def test_decorate_non_async_no_thread_argument() -> None:
    """Decorating a non-async method without saying explicitly that it's a thread is an error."""
    with pytest.raises(WorkerDeclarationError):

        class _(App[None]):
            @work
            def foo(self) -> None:
                pass


def test_decorate_non_async_no_thread_is_false() -> None:
    """Decorating a non-async method and saying it isn't a thread is an error."""
    with pytest.raises(WorkerDeclarationError):

        class _(App[None]):
            @work(thread=False)
            def foo(self) -> None:
                pass
