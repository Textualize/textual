from __future__ import annotations

import asyncio
import enum
from abc import ABC, abstractmethod
from contextvars import ContextVar
from typing import TYPE_CHECKING, Any, Callable, Coroutine

if TYPE_CHECKING:
    from .app import App


active_worker: ContextVar[Worker] = ContextVar("active_worker")


class WorkerState(enum.Enum):
    """A description of the worker's current state."""

    READY = 1
    RUNNING = 2
    CANCELLED = 3
    ERROR = 4
    SUCCESS = 5


class Worker(ABC):
    def __init__(
        self, name: str = "", group: str = "default", auto_cancel: bool = False
    ) -> None:
        self.name = name
        self.group = group
        self.auto_cancel = auto_cancel
        self._state = WorkerState.READY
        self._error: Exception | None = None
        self._step: int = 0
        self._total_steps: int = 0
        self._message: str | None = None

    @property
    def state(self) -> WorkerState:
        return self._state

    @property
    def message(self) -> str | None:
        return self._message

    @message.setter
    def message(self, message: str) -> None:
        self._message = message

    @abstractmethod
    async def _start(self, app: App, done_callback: Callable[[Worker], None]) -> None:
        ...

    @abstractmethod
    def cancel(self) -> None:
        ...

    @abstractmethod
    async def _wait(self) -> None:
        ...


class AsyncWorker(Worker):
    def __init__(
        self,
        work_function: Callable[[], Coroutine] | None = None,
        *,
        name: str = "",
        group: str = "default",
    ) -> None:
        self._work_function = work_function
        self._task: asyncio.Task | None = None
        super().__init__(name=name, group=group)

    async def run(self) -> None:
        """Run the work.

        Implement this method in a subclass, or pass a callable to the constructor.

        """
        if self._work_function is not None:
            await self._work_function()

    async def _run(self, app: App) -> None:
        app._set_active()
        active_worker.set(self)

        self._state = WorkerState.RUNNING
        try:
            await self.run()
        except Exception as error:
            self._state = WorkerState.ERROR
            self._error = error
        except asyncio.CancelledError:
            self._state = WorkerState.CANCELLED
        else:
            self._state = WorkerState.SUCCESS

    async def _start(self, app: App, done_callback: Callable[[Worker], None]) -> None:
        self._task = asyncio.create_task(self._run(app))

        def task_done_callback(_task: asyncio.Task):
            done_callback(self)

        self._task.add_done_callback(task_done_callback)

    async def _wait(self) -> None:
        if self._task is not None:
            await self._task
