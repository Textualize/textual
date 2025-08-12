"""

This module contains the `Pilot` class used by [App.run_test][textual.app.App.run_test] to programmatically operate an app.

See the guide on how to [test Textual apps](/guide/testing).

"""

from __future__ import annotations

import asyncio
from typing import Any, Generic

import rich.repr

from textual._wait import wait_for_idle
from textual.app import App, ReturnType
from textual.drivers.headless_driver import HeadlessDriver
from textual.events import Click, MouseDown, MouseEvent, MouseMove, MouseUp, Resize
from textual.geometry import Offset, Size
from textual.widget import Widget


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
        "widget": target,
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

    async def resize_terminal(self, width: int, height: int) -> None:
        """Resize the terminal to the given dimensions.

        Args:
            width: The new width of the terminal.
            height: The new height of the terminal.
        """
        size = Size(width, height)
        # If we're running with the headless driver, update the inherent app size.
        if isinstance(self.app._driver, HeadlessDriver):
            self.app._driver._size = size
        self.app.post_message(Resize(size, size))
        await self.pause()

    async def mouse_down(
        self,
        widget: Widget | type[Widget] | str | None = None,
        offset: tuple[int, int] = (0, 0),
        shift: bool = False,
        meta: bool = False,
        control: bool = False,
    ) -> bool:
        """Simulate a [`MouseDown`][textual.events.MouseDown] event at a specified position.

        The final position for the event is computed based on the selector provided and
        the offset specified and it must be within the visible area of the screen.

        Args:
            widget: A widget or selector used as an origin
                for the event offset. If this is not specified, the offset is interpreted
                relative to the screen. You can use this parameter to try to target a
                specific widget. However, if the widget is currently hidden or obscured by
                another widget, the event may not land on the widget you specified.
            offset: The offset for the event. The offset is relative to the selector / widget
                provided or to the screen, if no selector is provided.
            shift: Simulate the event with the shift key held down.
            meta: Simulate the event with the meta key held down.
            control: Simulate the event with the control key held down.

        Raises:
            OutOfBounds: If the position for the event is outside of the (visible) screen.

        Returns:
            True if no selector was specified or if the event landed on the selected
                widget, False otherwise.
        """
        try:
            return await self._post_mouse_events(
                [MouseMove, MouseDown],
                widget=widget,
                offset=offset,
                button=1,
                shift=shift,
                meta=meta,
                control=control,
            )
        except OutOfBounds as error:
            raise error from None

    async def mouse_up(
        self,
        widget: Widget | type[Widget] | str | None = None,
        offset: tuple[int, int] = (0, 0),
        shift: bool = False,
        meta: bool = False,
        control: bool = False,
    ) -> bool:
        """Simulate a [`MouseUp`][textual.events.MouseUp] event at a specified position.

        The final position for the event is computed based on the selector provided and
        the offset specified and it must be within the visible area of the screen.

        Args:
            widget: A widget or selector used as an origin
                for the event offset. If this is not specified, the offset is interpreted
                relative to the screen. You can use this parameter to try to target a
                specific widget. However, if the widget is currently hidden or obscured by
                another widget, the event may not land on the widget you specified.
            offset: The offset for the event. The offset is relative to the widget / selector
                provided or to the screen, if no selector is provided.
            shift: Simulate the event with the shift key held down.
            meta: Simulate the event with the meta key held down.
            control: Simulate the event with the control key held down.

        Raises:
            OutOfBounds: If the position for the event is outside of the (visible) screen.

        Returns:
            True if no selector was specified or if the event landed on the selected
                widget, False otherwise.
        """
        try:
            return await self._post_mouse_events(
                [MouseMove, MouseUp],
                widget=widget,
                offset=offset,
                button=1,
                shift=shift,
                meta=meta,
                control=control,
            )
        except OutOfBounds as error:
            raise error from None

    async def click(
        self,
        widget: Widget | type[Widget] | str | None = None,
        offset: tuple[int, int] = (0, 0),
        shift: bool = False,
        meta: bool = False,
        control: bool = False,
        times: int = 1,
    ) -> bool:
        """Simulate clicking with the mouse at a specified position.

        The final position to be clicked is computed based on the selector provided and
        the offset specified and it must be within the visible area of the screen.

        Implementation note: This method bypasses the normal event processing in `App.on_event`.

        Example:
            The code below runs an app and clicks its only button right in the middle:
            ```py
            async with SingleButtonApp().run_test() as pilot:
                await pilot.click(Button, offset=(8, 1))
            ```

        Args:
            widget: A widget or selector used as an origin
                for the click offset. If this is not specified, the offset is interpreted
                relative to the screen. You can use this parameter to try to click on a
                specific widget. However, if the widget is currently hidden or obscured by
                another widget, the click may not land on the widget you specified.
            offset: The offset to click. The offset is relative to the widget / selector provided
                or to the screen, if no selector is provided.
            shift: Click with the shift key held down.
            meta: Click with the meta key held down.
            control: Click with the control key held down.
            times: The number of times to click. 2 will double-click, 3 will triple-click, etc.

        Raises:
            OutOfBounds: If the position to be clicked is outside of the (visible) screen.

        Returns:
            True if no selector was specified or if the click landed on the selected
                widget, False otherwise.
        """
        try:
            return await self._post_mouse_events(
                [MouseDown, MouseUp, Click],
                widget=widget,
                offset=offset,
                button=1,
                shift=shift,
                meta=meta,
                control=control,
                times=times,
            )
        except OutOfBounds as error:
            raise error from None

    async def double_click(
        self,
        widget: Widget | type[Widget] | str | None = None,
        offset: tuple[int, int] = (0, 0),
        shift: bool = False,
        meta: bool = False,
        control: bool = False,
    ) -> bool:
        """Simulate double clicking with the mouse at a specified position.

        Alias for `pilot.click(..., times=2)`.

        The final position to be clicked is computed based on the selector provided and
        the offset specified and it must be within the visible area of the screen.

        Implementation note: This method bypasses the normal event processing in `App.on_event`.

        Example:
            The code below runs an app and double-clicks its only button right in the middle:
            ```py
            async with SingleButtonApp().run_test() as pilot:
                await pilot.double_click(Button, offset=(8, 1))
            ```

        Args:
            widget: A widget or selector used as an origin
                for the click offset. If this is not specified, the offset is interpreted
                relative to the screen. You can use this parameter to try to click on a
                specific widget. However, if the widget is currently hidden or obscured by
                another widget, the click may not land on the widget you specified.
            offset: The offset to click. The offset is relative to the widget / selector provided
                or to the screen, if no selector is provided.
            shift: Click with the shift key held down.
            meta: Click with the meta key held down.
            control: Click with the control key held down.

        Raises:
            OutOfBounds: If the position to be clicked is outside of the (visible) screen.

        Returns:
            True if no selector was specified or if the clicks landed on the selected
                widget, False otherwise.
        """
        return await self.click(widget, offset, shift, meta, control, times=2)

    async def triple_click(
        self,
        widget: Widget | type[Widget] | str | None = None,
        offset: tuple[int, int] = (0, 0),
        shift: bool = False,
        meta: bool = False,
        control: bool = False,
    ) -> bool:
        """Simulate triple clicking with the mouse at a specified position.

        Alias for `pilot.click(..., times=3)`.

        The final position to be clicked is computed based on the selector provided and
        the offset specified and it must be within the visible area of the screen.

        Implementation note: This method bypasses the normal event processing in `App.on_event`.

        Example:
            The code below runs an app and triple-clicks its only button right in the middle:
            ```py
            async with SingleButtonApp().run_test() as pilot:
                await pilot.triple_click(Button, offset=(8, 1))
            ```

        Args:
            widget: A widget or selector used as an origin
                for the click offset. If this is not specified, the offset is interpreted
                relative to the screen. You can use this parameter to try to click on a
                specific widget. However, if the widget is currently hidden or obscured by
                another widget, the click may not land on the widget you specified.
            offset: The offset to click. The offset is relative to the widget / selector provided
                or to the screen, if no selector is provided.
            shift: Click with the shift key held down.
            meta: Click with the meta key held down.
            control: Click with the control key held down.

        Raises:
            OutOfBounds: If the position to be clicked is outside of the (visible) screen.

        Returns:
            True if no selector was specified or if the clicks landed on the selected
                widget, False otherwise.
        """
        return await self.click(widget, offset, shift, meta, control, times=3)

    async def hover(
        self,
        widget: Widget | type[Widget] | str | None | None = None,
        offset: tuple[int, int] = (0, 0),
    ) -> bool:
        """Simulate hovering with the mouse cursor at a specified position.

        The final position to be hovered is computed based on the selector provided and
        the offset specified and it must be within the visible area of the screen.

        Args:
            widget: A widget or selector used as an origin
                for the hover offset. If this is not specified, the offset is interpreted
                relative to the screen. You can use this parameter to try to hover a
                specific widget. However, if the widget is currently hidden or obscured by
                another widget, the hover may not land on the widget you specified.
            offset: The offset to hover. The offset is relative to the widget / selector provided
                or to the screen, if no selector is provided.

        Raises:
            OutOfBounds: If the position to be hovered is outside of the (visible) screen.

        Returns:
            True if no selector was specified or if the hover landed on the selected
                widget, False otherwise.
        """
        # This is usually what the user wants because it gives time for the mouse to
        # "settle" before moving it to the new hover position.
        await self.pause()
        try:
            return await self._post_mouse_events([MouseMove], widget, offset, button=0)
        except OutOfBounds as error:
            raise error from None

    async def _post_mouse_events(
        self,
        events: list[type[MouseEvent]],
        widget: Widget | type[Widget] | str | None | None = None,
        offset: tuple[int, int] = (0, 0),
        button: int = 0,
        shift: bool = False,
        meta: bool = False,
        control: bool = False,
        times: int = 1,
    ) -> bool:
        """Simulate a series of mouse events to be fired at a given position.

        The final position for the events is computed based on the selector provided and
        the offset specified and it must be within the visible area of the screen.

        This function abstracts away the commonalities of the other mouse event-related
        functions that the pilot exposes.

        Args:
            widget: A widget or selector used as the origin
                for the event's offset. If this is not specified, the offset is interpreted
                relative to the screen. You can use this parameter to try to target a
                specific widget. However, if the widget is currently hidden or obscured by
                another widget, the events may not land on the widget you specified.
            offset: The offset for the events. The offset is relative to the widget / selector
                provided or to the screen, if no selector is provided.
            shift: Simulate the events with the shift key held down.
            meta: Simulate the events with the meta key held down.
            control: Simulate the events with the control key held down.
            times: The number of times to click. 2 will double-click, 3 will triple-click, etc.
        Raises:
            OutOfBounds: If the position for the events is outside of the (visible) screen.

        Returns:
            True if no selector was specified or if the *final* event landed on the
                selected widget, False otherwise.
        """
        app = self.app
        screen = app.screen
        target_widget: Widget
        if widget is None:
            target_widget = screen
        elif isinstance(widget, Widget):
            target_widget = widget
        else:
            target_widget = app.screen.query_one(widget)

        message_arguments = _get_mouse_message_arguments(
            target_widget,
            offset,
            button=button,
            shift=shift,
            meta=meta,
            control=control,
        )

        offset = Offset(message_arguments["x"], message_arguments["y"])
        if offset not in screen.region:
            raise OutOfBounds(
                "Target offset is outside of currently-visible screen region."
            )

        widget_at = None
        for chain in range(1, times + 1):
            for mouse_event_cls in events:
                # Get the widget under the mouse before the event because the app might
                # react to the event and move things around. We override on each iteration
                # because we assume the final event in `events` is the actual event we care
                # about and that all the preceding events are just setup.
                # E.g., the click event is preceded by MouseDown/MouseUp to emulate how
                # the driver works and emits a click event.
                kwargs = message_arguments
                if mouse_event_cls is Click:
                    kwargs = {**kwargs, "chain": chain}

                widget_at, _ = app.get_widget_at(*offset)
                event = mouse_event_cls(**kwargs)
                # Bypass event processing in App.on_event. Because App.on_event
                # is responsible for updating App.mouse_position, and because
                # that's useful to other things (tooltip handling, for example),
                # we patch the offset in there as well.
                app.mouse_position = offset
                screen._forward_event(event)
                await self.pause()

        return widget is None or widget_at is target_widget

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
        try:
            screen = self.app.screen
        except Exception:
            return False
        children = [self.app, *screen.walk_children(with_self=True)]
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
