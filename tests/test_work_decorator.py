import asyncio
from time import sleep
from typing import Callable

import pytest

from textual import work
from textual._work_decorator import WorkerDeclarationError
from textual.app import App
from textual.worker import Worker, WorkerState, WorkType


class WorkApp(App):
    worker: Worker

    def __init__(self) -> None:
        super().__init__()
        self.states: list[WorkerState] = []

    @work
    async def async_work(self) -> str:
        await asyncio.sleep(0.1)
        return "foo"

    @work(thread=True)
    async def async_thread_work(self) -> str:
        await asyncio.sleep(0.1)
        return "foo"

    @work(thread=True)
    def thread_work(self) -> str:
        sleep(0.1)
        return "foo"

    def launch(self, worker) -> None:
        self.worker = worker()

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        self.states.append(event.state)


async def work_with(launcher: Callable[[WorkApp], WorkType]) -> None:
    """Core code for testing a work decorator."""
    app = WorkApp()
    async with app.run_test() as pilot:
        app.launch(launcher(app))
        await app.workers.wait_for_complete()
        result = await app.worker.wait()
        assert result == "foo"
        await pilot.pause()
        assert app.states == [
            WorkerState.PENDING,
            WorkerState.RUNNING,
            WorkerState.SUCCESS,
        ]


async def test_async_work() -> None:
    """It should be possible to decorate an async method as an async worker."""
    await work_with(lambda app: app.async_work)


async def test_async_thread_work() -> None:
    """It should be possible to decorate an async method as a thread worker."""
    await work_with(lambda app: app.async_thread_work)


async def test_thread_work() -> None:
    """It should be possible to decorate a non-async method as a thread worker."""
    await work_with(lambda app: app.thread_work)


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
