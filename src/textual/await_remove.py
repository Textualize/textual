"""
An *optionally* awaitable object returned by methods that remove widgets.
"""

from asyncio import Event, Task
from typing import Generator


class AwaitRemove:
    """An awaitable returned by a method that removes DOM nodes.

    Returned by [Widget.remove][textual.widget.Widget.remove] and
    [DOMQuery.remove][textual.css.query.DOMQuery.remove].
    """

    def __init__(self, finished_flag: Event, task: Task) -> None:
        """Initialise the instance of ``AwaitRemove``.

        Args:
            finished_flag: The asyncio event to wait on.
            task: The task which does the remove (required to keep a reference).
        """
        self.finished_flag = finished_flag
        self._task = task

    async def __call__(self) -> None:
        await self

    def __await__(self) -> Generator[None, None, None]:
        async def await_prune() -> None:
            """Wait for the prune operation to finish."""
            await self.finished_flag.wait()

        return await_prune().__await__()
