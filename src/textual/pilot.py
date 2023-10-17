"""

The pilot object is used by [App.run_test][textual.app.App.run_test] to programmatically operate an app.

See the guide on how to [test Textual apps](/guide/testing).

"""

from __future__ import annotations

import asyncio
from typing import Any, Generic

import rich.repr

from ._wait import wait_for_idle
from .app import App, ReturnType
from .events import Click, MouseDown, MouseMove, MouseUp
from .geometry import Offset
from .widget import Widget


def _get_mouse_message_arguments(
    target: Widget,
    offset: tuple[int, int] = (0, 0),
    button: int = 0,
    shift: bool = False,
    meta: bool = False,
    control: bool = False,
) -> dict[str, Any]:
    """Get the arguments to pass into mouse messages for the click and hover methods."""
    click_x, click_y = target.region.offset + offset
    message_arguments = {
        "x": click_x,
        "y": click_y,
        "delta_x": 0,
        "delta_y": 0,
        "button": button,
        "shift": shift,
        "meta": meta,
        "ctrl": control,
        "screen_x": click_x,
        "screen_y": click_y,
    }
    return message_arguments


class OutOfBounds(Exception):
    """Raised when the pilot mouse target is outside of the (visible) screen."""


class WaitForScreenTimeout(Exception):
    """Exception raised if messages aren't being processed quickly enough.

    If this occurs, the most likely explanation is some kind of deadlock in the app code.
    """


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
            await self._wait_for_screen()

    async def click(
        self,
        selector: type[Widget] | str | None = None,
        offset: tuple[int, int] = (0, 0),
        shift: bool = False,
        meta: bool = False,
        control: bool = False,
    ) -> bool:
        """Simulate clicking with the mouse at a specified position.

        The final position to be clicked is computed based on the selector provided and
        the offset specified and it must be within the visible area of the screen.

        Args:
            selector: A selector to specify a widget that should be used as the reference
                for the click offset. If this is not specified, the offset is interpreted
                relative to the screen. You can use this parameter to try to click on a
                specific widget. However, if the widget is currently hidden or obscured by
                another widget, the click may not land on the widget you specified.
            offset: The offset to click. The offset is relative to the selector provided
                or to the screen, if no selector is provided.
            shift: Click with the shift key held down.
            meta: Click with the meta key held down.
            control: Click with the control key held down.

        Raises:
            OutOfBounds: If the position to be clicked is outside of the (visible) screen.

        Returns:
            True if no selector was specified or if the click landed on the selected
                widget, False otherwise.
        """
        app = self.app
        screen = app.screen
        if selector is not None:
            target_widget = app.query_one(selector)
        else:
            target_widget = screen

        message_arguments = _get_mouse_message_arguments(
            target_widget, offset, button=1, shift=shift, meta=meta, control=control
        )

        click_offset = Offset(message_arguments["x"], message_arguments["y"])
        if click_offset not in screen.region:
            raise OutOfBounds(
                "Target offset is outside of currently-visible screen region."
            )

        app.post_message(MouseDown(**message_arguments))
        await self.pause()
        app.post_message(MouseUp(**message_arguments))
        await self.pause()

        # Figure out the widget under the click before we click because the app
        # might react to the click and move things.
        widget_at, _ = app.get_widget_at(*click_offset)
        app.post_message(Click(**message_arguments))
        await self.pause()

        return selector is None or widget_at is target_widget

    async def hover(
        self,
        selector: type[Widget] | str | None | None = None,
        offset: tuple[int, int] = (0, 0),
    ) -> bool:
        """Simulate hovering with the mouse cursor at a specified position.

        The final position to be hovered is computed based on the selector provided and
        the offset specified and it must be within the visible area of the screen.

        Args:
            selector: A selector to specify a widget that should be used as the reference
                for the hover offset. If this is not specified, the offset is interpreted
                relative to the screen. You can use this parameter to try to hover a
                specific widget. However, if the widget is currently hidden or obscured by
                another widget, the hover may not land on the widget you specified.
            offset: The offset to hover. The offset is relative to the selector provided
                or to the screen, if no selector is provided.

        Raises:
            OutOfBounds: If the position to be hovered is outside of the (visible) screen.

        Returns:
            True if no selector was specified or if the hover landed on the selected
                widget, False otherwise.
        """
        app = self.app
        screen = app.screen
        if selector is not None:
            target_widget = app.query_one(selector)
        else:
            target_widget = screen

        message_arguments = _get_mouse_message_arguments(
            target_widget, offset, button=0
        )

        hover_offset = Offset(message_arguments["x"], message_arguments["y"])
        if hover_offset not in screen.region:
            raise OutOfBounds(
                "Target offset is outside of currently-visible screen region."
            )

        await self.pause()
        app.post_message(MouseMove(**message_arguments))
        await self.pause()

        widget_at, _ = app.get_widget_at(*hover_offset)
        return selector is None or widget_at is target_widget

    async def _wait_for_screen(self, timeout: float = 30.0) -> bool:
        """Wait for the current screen and its children to have processed all pending events.

        Args:
            timeout: A timeout in seconds to wait.

        Returns:
            `True` if all events were processed. `False` if an exception occurred,
            meaning that not all events could be processed.

        Raises:
            WaitForScreenTimeout: If the screen and its children didn't finish processing within the timeout.
        """
        children = [self.app, *self.app.screen.walk_children(with_self=True)]
        count = 0
        count_zero_event = asyncio.Event()

        def decrement_counter() -> None:
            """Decrement internal counter, and set an event if it reaches zero."""
            nonlocal count
            count -= 1
            if count == 0:
                # When count is zero, all messages queued at the start of the method have been processed
                count_zero_event.set()

        # Increase the count for every successful call_later
        for child in children:
            if child.call_later(decrement_counter):
                count += 1

        if count:
            # Wait for the count to return to zero, or a timeout, or an exception
            wait_for = [
                asyncio.create_task(count_zero_event.wait()),
                asyncio.create_task(self.app._exception_event.wait()),
            ]
            _, pending = await asyncio.wait(
                wait_for,
                timeout=timeout,
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()

            timed_out = len(wait_for) == len(pending)
            if timed_out:
                raise WaitForScreenTimeout(
                    "Timed out while waiting for widgets to process pending messages."
                )

            # We've either timed out, encountered an exception, or we've finished
            # decrementing all the counters (all events processed in children).
            if count > 0:
                return False

        return True

    async def pause(self, delay: float | None = None) -> None:
        """Insert a pause.

        Args:
            delay: Seconds to pause, or None to wait for cpu idle.
        """
        # These sleep zeros, are to force asyncio to give up a time-slice.
        await self._wait_for_screen()
        if delay is None:
            await wait_for_idle(0)
        else:
            await asyncio.sleep(delay)
        self.app.screen._on_timer_update()

    async def wait_for_animation(self) -> None:
        """Wait for any current animation to complete."""
        await self._app.animator.wait_for_idle()
        self.app.screen._on_timer_update()

    async def wait_for_scheduled_animations(self) -> None:
        """Wait for any current and scheduled animations to complete."""
        await self._wait_for_screen()
        await self._app.animator.wait_until_complete()
        await self._wait_for_screen()
        await wait_for_idle()
        self.app.screen._on_timer_update()

    async def exit(self, result: ReturnType) -> None:
        """Exit the app with the given result.

        Args:
            result: The app result returned by `run` or `run_async`.
        """
        await self._wait_for_screen()
        await wait_for_idle()
        self.app.exit(result)
