import asyncio
from time import sleep
from typing import Callable, List, Tuple

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


class NestedWorkersApp(App[None]):
    def __init__(self, call_stack: List[str]):
        self.call_stack = call_stack
        super().__init__()

    def call_from_stack(self):
        if self.call_stack:
            call_now = self.call_stack.pop()
            getattr(self, call_now)()

    @work(thread=False)
    async def async_no_thread(self):
        self.call_from_stack()

    @work(thread=True)
    async def async_thread(self):
        self.call_from_stack()

    @work(thread=True)
    def thread(self):
        self.call_from_stack()


@pytest.mark.parametrize(
    "call_stack",
    [  # from itertools import product; list(product("async_no_thread async_thread thread".split(), repeat=3))
        ("async_no_thread", "async_no_thread", "async_no_thread"),
        ("async_no_thread", "async_no_thread", "async_thread"),
        ("async_no_thread", "async_no_thread", "thread"),
        ("async_no_thread", "async_thread", "async_no_thread"),
        ("async_no_thread", "async_thread", "async_thread"),
        ("async_no_thread", "async_thread", "thread"),
        ("async_no_thread", "thread", "async_no_thread"),
        ("async_no_thread", "thread", "async_thread"),
        ("async_no_thread", "thread", "thread"),
        ("async_thread", "async_no_thread", "async_no_thread"),
        ("async_thread", "async_no_thread", "async_thread"),
        ("async_thread", "async_no_thread", "thread"),
        ("async_thread", "async_thread", "async_no_thread"),
        ("async_thread", "async_thread", "async_thread"),
        ("async_thread", "async_thread", "thread"),
        ("async_thread", "thread", "async_no_thread"),
        ("async_thread", "thread", "async_thread"),
        ("async_thread", "thread", "thread"),
        ("thread", "async_no_thread", "async_no_thread"),
        ("thread", "async_no_thread", "async_thread"),
        ("thread", "async_no_thread", "thread"),
        ("thread", "async_thread", "async_no_thread"),
        ("thread", "async_thread", "async_thread"),
        ("thread", "async_thread", "thread"),
        ("thread", "thread", "async_no_thread"),
        ("thread", "thread", "async_thread"),
        ("thread", "thread", "thread"),
        (  # Plus a longer chain to stress test this mechanism.
            "async_no_thread",
            "async_no_thread",
            "thread",
            "thread",
            "async_thread",
            "async_thread",
            "async_no_thread",
            "async_thread",
            "async_no_thread",
            "async_thread",
            "thread",
            "async_thread",
            "async_thread",
            "async_no_thread",
            "async_no_thread",
            "thread",
            "thread",
            "async_no_thread",
            "async_no_thread",
            "thread",
            "async_no_thread",
            "thread",
            "thread",
        ),
    ],
)
async def test_calling_workers_from_within_workers(call_stack: Tuple[str]):
    """Regression test for https://github.com/Textualize/textual/issues/3472.

    This makes sure we can nest worker calls without a problem.
    """
    app = NestedWorkersApp(list(call_stack))
    async with app.run_test():
        app.call_from_stack()
        # We need multiple awaits because we're creating a chain of workers that may
        # have multiple async workers, each of which may need the await to have enough
        # time to call the next one in the chain.
        for _ in range(len(call_stack)):
            await app.workers.wait_for_complete()
        assert app.call_stack == []
