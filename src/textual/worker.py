"""
This module contains the `Worker` class and related objects.

See the guide for how to use [workers](/guide/workers).

"""

from __future__ import annotations

import asyncio
import enum
import inspect
from contextvars import ContextVar
from threading import Event
from time import monotonic
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    Coroutine,
    Generic,
    TypeVar,
    Union,
    cast,
)

import rich.repr
from typing_extensions import TypeAlias

from textual.message import Message

if TYPE_CHECKING:
    from textual.app import App
    from textual.dom import DOMNode


active_worker: ContextVar[Worker] = ContextVar("active_worker")
"""Currently active worker context var."""


class NoActiveWorker(Exception):
    """There is no active worker."""


class WorkerError(Exception):
    """A worker related error."""


class WorkerFailed(WorkerError):
    """The worker raised an exception and did not complete."""

    def __init__(self, error: BaseException) -> None:
        self.error = error
        super().__init__(f"Worker raised exception: {error!r}")


class DeadlockError(WorkerError):
    """The operation would result in a deadlock."""


class WorkerCancelled(WorkerError):
    """The worker was cancelled and did not complete."""


def get_current_worker() -> Worker:
    """Get the currently active worker.

    Raises:
        NoActiveWorker: If there is no active worker.

    Returns:
        A Worker instance.
    """
    try:
        return active_worker.get()
    except LookupError:
        raise NoActiveWorker(
            "There is no active worker in this task or thread."
        ) from None


class WorkerState(enum.Enum):
    """A description of the worker's current state."""

    PENDING = 1
    """Worker is initialized, but not running."""
    RUNNING = 2
    """Worker is running."""
    CANCELLED = 3
    """Worker is not running, and was cancelled."""
    ERROR = 4
    """Worker is not running, and exited with an error."""
    SUCCESS = 5
    """Worker is not running, and completed successfully."""


ResultType = TypeVar("ResultType")


WorkType: TypeAlias = Union[
    Callable[[], Coroutine[None, None, ResultType]],
    Callable[[], ResultType],
    Awaitable[ResultType],
]
"""Type used for [workers](/guide/workers/)."""


class _ReprText:
    """Shim to insert a word into the Worker's repr."""

    def __init__(self, text: str) -> None:
        self.text = text

    def __repr__(self) -> str:
        return self.text


@rich.repr.auto(angular=True)
class Worker(Generic[ResultType]):
    """A class to manage concurrent work (either a task or a thread)."""

    @rich.repr.auto
    class StateChanged(Message, bubble=False, namespace="worker"):
        """The worker state changed."""

        def __init__(self, worker: Worker, state: WorkerState) -> None:
            """Initialize the StateChanged message.

            Args:
                worker: The worker object.
                state: New state.
            """
            self.worker = worker
            self.state = state
            super().__init__()

        def __rich_repr__(self) -> rich.repr.Result:
            yield self.worker
            yield self.state

    def __init__(
        self,
        node: DOMNode,
        work: WorkType,
        *,
        name: str = "",
        group: str = "default",
        description: str = "",
        exit_on_error: bool = True,
        thread: bool = False,
    ) -> None:
        """Initialize a Worker.

        Args:
            node: The widget, screen, or App that initiated the work.
            work: A callable, coroutine, or other awaitable object to run in the worker.
            name: Name of the worker (short string to help identify when debugging).
            group: The worker group.
            description: Description of the worker (longer string with more details).
            exit_on_error: Exit the app if the worker raises an error. Set to `False` to suppress exceptions.
            thread: Mark the worker as a thread worker.
        """
        self._node = node
        self._work = work
        self.name = name
        self.group = group
        self.description = (
            description if len(description) <= 1000 else description[:1000] + "..."
        )
        self.exit_on_error = exit_on_error
        self.cancelled_event: Event = Event()
        """A threading event set when the worker is cancelled."""
        self._thread_worker = thread
        self._state = WorkerState.PENDING
        self.state = self._state
        self._error: BaseException | None = None
        self._completed_steps: int = 0
        self._total_steps: int | None = None
        self._cancelled: bool = False
        self._created_time = monotonic()
        self._result: ResultType | None = None
        self._task: asyncio.Task | None = None
        self._node.post_message(self.StateChanged(self, self._state))

    def __rich_repr__(self) -> rich.repr.Result:
        yield _ReprText(self.state.name)
        yield "name", self.name, ""
        yield "group", self.group, "default"
        yield "description", self.description, ""
        yield "progress", round(self.progress, 1), 0.0

    @property
    def node(self) -> DOMNode:
        """The node where this worker was run from."""
        return self._node

    @property
    def state(self) -> WorkerState:
        """The current state of the worker."""
        return self._state

    @state.setter
    def state(self, state: WorkerState) -> None:
        """Set the state, and send a message."""
        changed = state != self._state
        self._state = state
        if changed:
            self._node.post_message(self.StateChanged(self, state))

    @property
    def is_cancelled(self) -> bool:
        """Has the work been cancelled?

        Note that cancelled work may still be running.
        """
        return self._cancelled

    @property
    def is_running(self) -> bool:
        """Is the task running?"""
        return self.state == WorkerState.RUNNING

    @property
    def is_finished(self) -> bool:
        """Has the task finished (cancelled, error, or success)?"""
        return self.state in (
            WorkerState.CANCELLED,
            WorkerState.ERROR,
            WorkerState.SUCCESS,
        )

    @property
    def completed_steps(self) -> int:
        """The number of completed steps."""
        return self._completed_steps

    @property
    def total_steps(self) -> int | None:
        """The number of total steps, or None if indeterminate."""
        return self._total_steps

    @property
    def progress(self) -> float:
        """Progress as a percentage.

        If the total steps is None, then this will return 0. The percentage will be clamped between 0 and 100.
        """
        if not self._total_steps:
            return 0.0
        return max(0, min(100, (self._completed_steps / self._total_steps) * 100.0))

    @property
    def result(self) -> ResultType | None:
        """The result of the worker, or `None` if there is no result."""
        return self._result

    @property
    def error(self) -> BaseException | None:
        """The exception raised by the worker, or `None` if there was no error."""
        return self._error

    def update(
        self, completed_steps: int | None = None, total_steps: int | None = -1
    ) -> None:
        """Update the number of completed steps.

        Args:
            completed_steps: The number of completed seps, or `None` to not change.
            total_steps: The total number of steps, `None` for indeterminate, or -1 to leave unchanged.
        """
        if completed_steps is not None:
            self._completed_steps += completed_steps
        if total_steps != -1:
            self._total_steps = None if total_steps is None else max(0, total_steps)

    def advance(self, steps: int = 1) -> None:
        """Advance the number of completed steps.

        Args:
            steps: Number of steps to advance.
        """
        self._completed_steps += steps

    async def _run_threaded(self) -> ResultType:
        """Run a threaded worker.

        Returns:
            Return value of the work.
        """

        def run_awaitable(work: Awaitable[ResultType]) -> ResultType:
            """Set the active worker and await the awaitable."""

            async def do_work() -> ResultType:
                active_worker.set(self)
                return await work

            return asyncio.run(do_work())

        def run_coroutine(
            work: Callable[[], Coroutine[None, None, ResultType]],
        ) -> ResultType:
            """Set the active worker and await coroutine."""
            return run_awaitable(work())

        def run_callable(work: Callable[[], ResultType]) -> ResultType:
            """Set the active worker, and call the callable."""
            active_worker.set(self)
            return work()

        if (
            inspect.iscoroutinefunction(self._work)
            or hasattr(self._work, "func")
            and inspect.iscoroutinefunction(self._work.func)
        ):
            runner = run_coroutine
        elif inspect.isawaitable(self._work):
            runner = run_awaitable
        elif callable(self._work):
            runner = run_callable
        else:
            raise WorkerError("Unsupported attempt to run a thread worker")

        loop = asyncio.get_running_loop()
        assert loop is not None
        return await loop.run_in_executor(None, runner, self._work)

    async def _run_async(self) -> ResultType:
        """Run an async worker.

        Returns:
            Return value of the work.
        """
        if (
            inspect.iscoroutinefunction(self._work)
            or hasattr(self._work, "func")
            and inspect.iscoroutinefunction(self._work.func)
        ):
            return await self._work()
        elif inspect.isawaitable(self._work):
            return await self._work
        elif callable(self._work):
            raise WorkerError("Request to run a non-async function as an async worker")
        raise WorkerError("Unsupported attempt to run an async worker")

    async def run(self) -> ResultType:
        """Run the work.

        Implement this method in a subclass, or pass a callable to the constructor.

        Returns:
            Return value of the work.
        """
        return await (
            self._run_threaded() if self._thread_worker else self._run_async()
        )

    async def _run(self, app: App) -> None:
        """Run the worker.

        Args:
            app: App instance.
        """
        with app._context():
            active_worker.set(self)

            self.state = WorkerState.RUNNING
            app.log.worker(self)
            try:
                self._result = await self.run()
            except asyncio.CancelledError as error:
                self.state = WorkerState.CANCELLED
                self._error = error
                app.log.worker(self)
            except Exception as error:
                self.state = WorkerState.ERROR
                self._error = error
                app.log.worker(self, "failed", repr(error))
                from rich.traceback import Traceback

                app.log.worker(Traceback())
                if self.exit_on_error:
                    worker_failed = WorkerFailed(self._error)
                    app._handle_exception(worker_failed)
            else:
                self.state = WorkerState.SUCCESS
                app.log.worker(self)

    def _start(
        self, app: App, done_callback: Callable[[Worker], None] | None = None
    ) -> None:
        """Start the worker.

        Args:
            app: An app instance.
            done_callback: A callback to call when the task is done.
        """
        if self._task is not None:
            return
        self.state = WorkerState.RUNNING
        self._task = asyncio.create_task(self._run(app))

        def task_done_callback(_task: asyncio.Task) -> None:
            """Run the callback.

            Called by `Task.add_done_callback`.

            Args:
                The worker's task.
            """
            if done_callback is not None:
                done_callback(self)

        self._task.add_done_callback(task_done_callback)

    def cancel(self) -> None:
        """Cancel the task."""
        self._cancelled = True
        if self._task is not None:
            self._task.cancel()
        self.cancelled_event.set()

    async def wait(self) -> ResultType:
        """Wait for the work to complete.

        Raises:
            WorkerFailed: If the Worker raised an exception.
            WorkerCancelled: If the Worker was cancelled before it completed.

        Returns:
            The return value of the work.
        """
        try:
            if active_worker.get() is self:
                raise DeadlockError(
                    "Can't call worker.wait from within the worker function!"
                )
        except LookupError:
            # Not in a worker
            pass

        if self.state == WorkerState.PENDING:
            raise WorkerError("Worker must be started before calling this method.")
        if self._task is not None:
            try:
                await self._task
            except asyncio.CancelledError as error:
                self.state = WorkerState.CANCELLED
                self._error = error
        if self.state == WorkerState.ERROR:
            assert self._error is not None
            raise WorkerFailed(self._error)
        elif self.state == WorkerState.CANCELLED:
            raise WorkerCancelled("Worker was cancelled, and did not complete.")
        return cast("ResultType", self._result)
