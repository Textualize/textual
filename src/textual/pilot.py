from __future__ import annotations

import rich.repr

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import App


@rich.repr.auto(angular=True)
class Pilot:
    """Pilot object to drive an app."""

    def __init__(self, app: App) -> None:
        self._app = app

    def __rich_repr__(self) -> rich.repr.Result:
        yield "app", self._app

    @property
    def app(self) -> App:
        """Get a reference to the application.

        Returns:
            App: The App instance.
        """
        return self._app

    async def press(self, *keys: str) -> None:
        """Simulate key-presses.

        Args:
            *keys: Keys to press.

        """
        if keys:
            await self._app._press_keys(keys)

    async def pause(self, delay: float = 50 / 1000) -> None:
        """Insert a pause.

        Args:
            delay (float, optional): Seconds to pause. Defaults to 50ms.
        """
        await asyncio.sleep(delay)

    async def exit(self, result: object) -> None:
        """Exit the app with the given result.

        Args:
            result (object): The app result returned by `run` or `run_async`.
        """
        self.app.exit(result)
