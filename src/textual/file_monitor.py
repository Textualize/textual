from __future__ import annotations

import os
from pathlib import PurePath
from typing import Callable

import rich.repr

from ._callback import invoke


@rich.repr.auto
class FileMonitor:
    """Monitors files for changes and invokes a callback when it does."""

    def __init__(self, paths: list[PurePath], callback: Callable) -> None:
        self.paths = paths
        self.callback = callback
        self._modified = self._get_last_modified_time()

    def _get_last_modified_time(self) -> float:
        """Get the most recent modified time out of all files being watched."""
        return max(os.stat(path).st_mtime for path in self.paths)

    def check(self) -> bool:
        """Check the monitored files. Return True if any were changed since the last modification time."""
        modified = self._get_last_modified_time()
        changed = modified != self._modified
        self._modified = modified
        return changed

    async def __call__(self) -> None:
        if self.check():
            await self.on_change()

    async def on_change(self) -> None:
        """Called when any of the monitored files change."""
        await invoke(self.callback)
