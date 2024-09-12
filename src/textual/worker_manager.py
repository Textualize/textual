"""
Contains `WorkerManager`, a class to manage [workers](/guide/workers) for an app.

You access this object via [App.workers][textual.app.App.workers] or [Widget.workers][textual.dom.DOMNode.workers].
"""

from __future__ import annotations

import asyncio
from collections import Counter
from operator import attrgetter
from typing import TYPE_CHECKING, Any, Iterable, Iterator

import rich.repr

from textual.worker import Worker, WorkerState, WorkType

if TYPE_CHECKING:
    from textual.app import App
    from textual.dom import DOMNode


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

    def __iter__(self) -> Iterator[Worker[Any]]:
        return iter(sorted(self._workers, key=attrgetter("_created_time")))

    def __reversed__(self) -> Iterator[Worker[Any]]:
        return iter(
            sorted(self._workers, key=attrgetter("_created_time"), reverse=True)
        )

    def __bool__(self) -> bool:
        return bool(self._workers)

    def __len__(self) -> int:
        return len(self._workers)

    def __contains__(self, worker: object) -> bool:
        return worker in self._workers

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
            self.cancel_group(worker.node, worker.group)
        self._workers.add(worker)
        if start:
            worker._start(self._app, self._remove_worker)

    def _new_worker(
        self,
        work: WorkType,
        node: DOMNode,
        *,
        name: str | None = "",
        group: str = "default",
        description: str = "",
        exit_on_error: bool = True,
        start: bool = True,
        exclusive: bool = False,
        thread: bool = False,
    ) -> Worker:
        """Create a worker from a function, coroutine, or awaitable.

        Args:
            work: A callable, a coroutine, or other awaitable.
            name: A name to identify the worker.
            group: The worker group.
            description: A description of the worker.
            exit_on_error: Exit the app if the worker raises an error. Set to `False` to suppress exceptions.
            start: Automatically start the worker.
            exclusive: Cancel all workers in the same group.
            thread: Mark the worker as a thread worker.

        Returns:
            A Worker instance.
        """
        worker: Worker[Any] = Worker(
            node,
            work,
            name=name or getattr(work, "__name__", "") or "",
            group=group,
            description=description or repr(work),
            exit_on_error=exit_on_error,
            thread=thread,
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

    def cancel_group(self, node: DOMNode, group: str) -> list[Worker]:
        """Cancel a single group.

        Args:
            node: Worker DOM node.
            group: A group name.

        Returns:
            A list of workers that were cancelled.
        """
        workers = [
            worker
            for worker in self._workers
            if (worker.group == group and worker.node == node)
        ]
        for worker in workers:
            worker.cancel()
        return workers

    def cancel_node(self, node: DOMNode) -> list[Worker]:
        """Cancel all workers associated with a given node

        Args:
            node: A DOM node (widget, screen, or App).

        Returns:
            List of cancelled workers.
        """
        workers = [worker for worker in self._workers if worker.node == node]
        for worker in workers:
            worker.cancel()
        return workers

    async def wait_for_complete(self, workers: Iterable[Worker] | None = None) -> None:
        """Wait for workers to complete.

        Args:
            workers: An iterable of workers or None to wait for all workers in the manager.
        """
        try:
            await asyncio.gather(*[worker.wait() for worker in (workers or self)])
        except asyncio.CancelledError:
            pass
