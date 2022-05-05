from __future__ import annotations
import os
from pathlib import PurePath
from typing import Callable

import rich.repr

from ._callback import invoke


@rich.repr.auto
class FileMonitor:
    def __init__(self, path: str | PurePath, callback: Callable) -> None:
        self.path = path
        self.callback = callback
        self._modified = self._get_modified()

    def _get_modified(self) -> float:
        return os.stat(self.path).st_mtime

    def check(self) -> bool:
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
