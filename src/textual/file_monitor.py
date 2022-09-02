import os
from pathlib import PurePath
from typing import Callable

import rich.repr

from ._callback import invoke


@rich.repr.auto
class FileMonitor:
    """Monitors a file for changes and invokes a callback when it does."""

    def __init__(self, path: PurePath, callback: Callable) -> None:
        self.path = path
        self.callback = callback
        self._modified = self._get_modified()

    def _get_modified(self) -> float:
        """Get the modified time for a file being watched."""
        return os.stat(self.path).st_mtime

    def check(self) -> bool:
        """Check the monitored file. Return True if it was changed."""
        modified = self._get_modified()
        changed = modified != self._modified
        self._modified = modified
        return changed

    async def __call__(self) -> None:
        if self.check():
            await self.on_change()

    async def on_change(self) -> None:
        """Called when file changes."""
        await invoke(self.callback)
