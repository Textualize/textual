import asyncio
import time

from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.worker import Worker, WorkerState


def test_worker_manager_init():
    app = App()
    assert isinstance(repr(app.workers), str)
    assert not bool(app.workers)
    assert len(app.workers) == 0
    assert list(app.workers) == []
    assert list(reversed(app.workers)) == []


async def test_run_worker_async() -> None:
    """Check self.run_worker"""
    worker_events: list[Worker.StateChanged] = []

    work_result: str = ""

    new_worker: Worker

    class WorkerWidget(Widget):
        async def work(self) -> str:
            nonlocal work_result
            await asyncio.sleep(0.02)
            work_result = "foo"
            return "foo"

        def on_mount(self):
            nonlocal new_worker
            new_worker = self.run_worker(self.work, start=False)

        def on_worker_state_changed(self, event) -> None:
            worker_events.append(event)

    class WorkerApp(App):
        def compose(self) -> ComposeResult:
            yield WorkerWidget()

    app = WorkerApp()
    async with app.run_test():
        assert new_worker in app.workers
        assert len(app.workers) == 1
        app.workers.start_all()
        await app.workers.wait_for_complete()
        assert len(app.workers) == 0

    assert work_result == "foo"
    assert isinstance(worker_events[0].worker.node, WorkerWidget)
    states = [event.state for event in worker_events]
    assert states == [
        WorkerState.PENDING,
        WorkerState.RUNNING,
        WorkerState.SUCCESS,
    ]


async def test_run_worker_thread_non_async() -> None:
    """Check self.run_worker"""
    worker_events: list[Worker.StateChanged] = []

    work_result: str = ""

    class WorkerWidget(Widget):
        def work(self) -> str:
            nonlocal work_result
            time.sleep(0.02)
            work_result = "foo"
            return "foo"

        def on_mount(self):
            self.run_worker(self.work, thread=True)

        def on_worker_state_changed(self, event) -> None:
            worker_events.append(event)

    class WorkerApp(App):
        def compose(self) -> ComposeResult:
            yield WorkerWidget()

    app = WorkerApp()
    async with app.run_test():
        await app.workers.wait_for_complete()

    assert work_result == "foo"
    assert isinstance(worker_events[0].worker.node, WorkerWidget)
    states = [event.state for event in worker_events]
    assert states == [
        WorkerState.PENDING,
        WorkerState.RUNNING,
        WorkerState.SUCCESS,
    ]


async def test_run_worker_thread_async() -> None:
    """Check self.run_worker"""
    worker_events: list[Worker.StateChanged] = []

    work_result: str = ""

    class WorkerWidget(Widget):
        async def work(self) -> str:
            nonlocal work_result
            time.sleep(0.02)
            work_result = "foo"
            return "foo"

        def on_mount(self):
            self.run_worker(self.work, thread=True)

        def on_worker_state_changed(self, event) -> None:
            worker_events.append(event)

    class WorkerApp(App):
        def compose(self) -> ComposeResult:
            yield WorkerWidget()

    app = WorkerApp()
    async with app.run_test():
        await app.workers.wait_for_complete()

    assert work_result == "foo"
    assert isinstance(worker_events[0].worker.node, WorkerWidget)
    states = [event.state for event in worker_events]
    assert states == [
        WorkerState.PENDING,
        WorkerState.RUNNING,
        WorkerState.SUCCESS,
    ]
