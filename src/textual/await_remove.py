"""
An *optionally* awaitable object returned by methods that remove widgets.
"""

import asyncio
from asyncio import Task, gather
from typing import Generator

from ._callback import invoke
from ._types import CallbackType


class AwaitRemove:
    def __init__(self, tasks: list[Task], post_remove: CallbackType) -> None:
        self._tasks = tasks
        self._post_remove = post_remove

    async def __call__(self) -> None:
        await self

    def __await__(self) -> Generator[None, None, None]:
        current_task = asyncio.current_task()
        tasks = [task for task in self._tasks if task is not current_task]

        async def await_prune() -> None:
            """Wait for the prune operation to finish."""
            await gather(*tasks)
            if self._post_remove:
                await invoke(self._post_remove)

        return await_prune().__await__()
