from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, Iterable, Sequence

import rich.repr

from ._callback import invoke


@rich.repr.auto
class FileMonitor:
    """Monitors files for changes and invokes a callback when it does."""

    _paths: set[Path]

    def __init__(self, paths: Sequence[Path], callback: Callable[[], None]) -> None:
        """Monitor the given file paths for changes.

        Args:
            paths: Paths to monitor.
            callback: Callback to invoke if any of the paths change.
        """
        self._paths = set(paths)
        self.callback = callback
        self._modified = self._get_last_modified_time()

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._paths

    def _get_last_modified_time(self) -> float:
        """Get the most recent modified time out of all files being watched."""
        modified_times = []
        for path in self._paths:
            try:
                modified_time = os.stat(path).st_mtime
            except FileNotFoundError:
                modified_time = 0
            modified_times.append(modified_time)
        return max(modified_times, default=0)

    def check(self) -> bool:
        """Check the monitored files. Return True if any were changed since the last modification time."""
        modified = self._get_last_modified_time()
        changed = modified != self._modified
        self._modified = modified
        return changed

    def add_paths(self, paths: Iterable[Path]) -> None:
        """Adds paths to start being monitored.

        Args:
            paths: The paths to be monitored.
        """
        self._paths.update(paths)

    async def __call__(self) -> None:
        if self.check():
            await self.on_change()

    async def on_change(self) -> None:
        """Called when any of the monitored files change."""
        await invoke(self.callback)
