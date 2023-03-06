from __future__ import annotations

import asyncio
from typing import Any, Generic

import rich.repr

from ._wait import wait_for_idle
from .app import App, ReturnType
from .css.query import QueryType
from .events import Click, MouseDown, MouseMove, MouseUp
from .geometry import Offset
from .widget import Widget


def _get_mouse_message_arguments(
    target: Widget, offset: Offset = Offset(), button: int = 0
) -> dict[str, Any]:
    x, y = offset
    click_x, click_y, _, _ = target.region.translate(offset)
    message_arguments = {
        "x": x,
        "y": y,
        "delta_x": 0,
        "delta_y": 0,
        "button": button,
        "shift": False,
        "meta": False,
        "ctrl": False,
        "screen_x": click_x,
        "screen_y": click_y,
    }
    return message_arguments


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

    async def click(
        self, selector: QueryType | None = None, offset: Offset = Offset()
    ) -> None:
        """Simulate clicking with the mouse.

        Args:
            selector: The widget that should be clicked. If None, then the click
                will occur relative to the screen. Note that this simply causes
                a click to occur at the location of the widget. If the widget is
                currently hidden or obscured by another widget, then the click may
                not land on it.
            offset: The offset to click within the selected widget.
        """
        screen = self.app.screen
        if selector is not None:
            target_widget = screen.query_one(selector)
        else:
            target_widget = screen

        message_arguments = _get_mouse_message_arguments(
            target_widget, offset, button=1
        )
        target_widget.post_message(MouseDown(**message_arguments))
        target_widget.post_message(MouseUp(**message_arguments))
        target_widget.post_message(Click(**message_arguments))
        await self.pause()

    async def hover(
        self, selector: QueryType | None = None, offset: Offset = Offset()
    ) -> None:
        """Simulate hovering with the mouse cursor.

        Args:
            selector: The widget that should be hovered. If None, then the click
                will occur relative to the screen.
            offset: The offset to hover over within the selected widget.
        """
        screen = self.app.screen
        if selector is not None:
            target_widget = screen.query_one(selector)
        else:
            target_widget = screen

        message_arguments = _get_mouse_message_arguments(
            target_widget, offset, button=0
        )
        target_widget.post_message(MouseMove(**message_arguments))
        await self.pause()

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
