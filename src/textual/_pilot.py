from __future__ import annotations

import asyncio
from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from .app import App


class Pilot:
    def __init__(self, app: App) -> None:
        self._app = app

    async def press(self, *keys: str) -> None:
        """Simulate key-presses.

        Args:
            *key: Keys to press.

        """
        await self._app._press_keys(keys)

    async def pause(self, delay: float = 50 / 1000) -> None:
        """Insert a pause.

        Args:
            delay (float, optional): Seconds to pause. Defaults to 50ms.
        """
        await asyncio.sleep(delay)
