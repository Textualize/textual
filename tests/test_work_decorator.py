import asyncio

from textual import work
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
