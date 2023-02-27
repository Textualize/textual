from __future__ import annotations

import asyncio
from typing import Generic

import rich.repr

from ._wait import wait_for_idle
from .app import App, ReturnType


@rich.repr.auto(angular=True)
class Pilot(Generic[ReturnType]):
    """Pilot object to drive an app."""

    def __init__(self, app: App[ReturnType]) -> None:
        self._app = app

    def __rich_repr__(self) -> rich.repr.Result:
        yield "app", self._app

    @property
    def app(self) -> App[ReturnType]:
        """App: A reference to the application."""
        return self._app

    async def press(self, *keys: str) -> None:
        """Simulate key-presses.

        Args:
            *keys: Keys to press.

        """
        if keys:
            await self._app._press_keys(keys)

    async def pause(self, delay: float | None = None) -> None:
        """Insert a pause.

        Args:
            delay: Seconds to pause, or None to wait for cpu idle.
        """
        # These sleep zeros, are to force asyncio to give up a time-slice,
        if delay is None:
            await wait_for_idle(0)
        else:
            await asyncio.sleep(delay)

    async def wait_for_animation(self) -> None:
        """Wait for any current animation to complete."""
        await self._app.animator.wait_for_idle()

    async def wait_for_scheduled_animations(self) -> None:
        """Wait for any current and scheduled animations to complete."""
        await self._app.animator.wait_until_complete()
        await wait_for_idle()

    async def exit(self, result: ReturnType) -> None:
        """Exit the app with the given result.

        Args:
            result: The app result returned by `run` or `run_async`.
        """
        await wait_for_idle()
        self.app.exit(result)
