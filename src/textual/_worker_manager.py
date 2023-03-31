from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING, Any

import rich.repr

from .worker import Worker, WorkerState, WorkType

if TYPE_CHECKING:
    from .app import App


@rich.repr.auto(angular=True)
class WorkerManager:
    """An object to manager a number of workers.

    You will not have to construct this class manually, as widgets, screens, and apps
    have a worker manager accessibly via a `workers` attribute.

    """

    def __init__(self, app: App) -> None:
        """Initialize a worker manager.

        Args:
            app: An App instance.
        """
        self._app = app
        """A reference to the app."""
        self._workers: set[Worker] = set()
        """The workers being managed."""

    def __rich_repr__(self) -> rich.repr.Result:
        counter: Counter[WorkerState] = Counter()
        counter.update(worker.state for worker in self._workers)
        for state, count in sorted(counter.items()):
            yield state.name, count

    def add_worker(
        self, worker: Worker, start: bool = True, exclusive: bool = True
    ) -> None:
        """Add a new worker.

        Args:
            worker: A Worker instance.
            start: Start the worker if True, otherwise the worker must be started manually.
            exclusive: Cancel all workers in the same group as `worker`.
        """
        if exclusive and worker.group:
            self.cancel_group(worker.group)
        self._workers.add(worker)
        if start:
            worker._start(self._app, self._remove_worker)

    def _run(
        self,
        work: WorkType,
        *,
        name: str | None = "",
        group: str = "default",
        description: str = "",
        start: bool = True,
        exclusive: bool = False,
    ) -> Worker:
        """Create a worker from a function, coroutine, or awaitable.

        Args:
            work: A callable, a coroutine, or other awaitable.
            name: A name to identify the worker.
            group: The worker group.
            description: A description of the worker.
            start: Automatically start the worker.
            exclusive: Cancel all workers in the same group.

        Returns:
            A Worker instance.
        """
        worker: Worker[Any] = Worker(
            work,
            name=name or getattr(work, "__name__", "") or "",
            group=group,
            description=description or repr(work),
        )
        self.add_worker(worker, start=start, exclusive=exclusive)
        return worker

    def _remove_worker(self, worker: Worker) -> None:
        """Remove a worker from the manager.

        Args:
            worker: A Worker instance.
        """
        self._workers.discard(worker)

    def start_all(self) -> None:
        """Start all the workers."""
        for worker in self._workers:
            worker._start(self._app, self._remove_worker)

    def cancel_all(self) -> None:
        """Cancel all workers."""
        for worker in self._workers:
            worker.cancel()

    def cancel_group(self, group: str) -> list[Worker]:
        """Cancel a single group.

        Args:
            group: A group name.

        Return:
            A list of workers that were cancelled.
        """
        workers = [worker for worker in self._workers if worker.group == group]
        for worker in workers:
            worker.cancel()
        return workers
