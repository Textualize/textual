from __future__ import annotations

import asyncio
import contextlib
import io
from math import ceil
from pathlib import Path
from time import monotonic
from typing import AsyncContextManager, cast, ContextManager
from unittest import mock

from rich.console import Console

from textual import events, errors
from textual._ansi_sequences import SYNC_START
from textual._clock import _Clock
from textual.app import WINDOWS
from textual._context import active_app
from textual.app import App, ComposeResult
from textual.driver import Driver
from textual.geometry import Size, Region

# N.B. These classes would better be named TestApp/TestConsole/TestDriver/etc,
# but it makes pytest emit warning as it will try to collect them as classes containing test cases :-/


class AppTest(App):
    def __init__(
        self,
        *,
        test_name: str,
        size: Size,
        log_verbosity: int = 2,
    ):
        # Tests will log in "/tests/test.[test name].log":
        log_path = Path(__file__).parent.parent / f"test.{test_name}.log"
        super().__init__(
            driver_class=DriverTest,
            log_path=log_path,
            log_verbosity=log_verbosity,
            log_color_system="256",
        )

        # Let's disable all features by default
        self.features = frozenset()

        # We need this so the "start buffeting"` is always sent for a screen refresh,
        # whatever the environment:
        # (we use it to slice the output into distinct full screens displays)
        self._sync_available = True

        self._size = size
        self._console = ConsoleTest(width=size.width, height=size.height)
        self._error_console = ConsoleTest(width=size.width, height=size.height)

    def log_tree(self) -> None:
        """Handy shortcut when testing stuff"""
        self.log(self.tree)

    def compose(self) -> ComposeResult:
        raise NotImplementedError(
            "Create a subclass of TestApp and override its `compose()` method, rather than using TestApp directly"
        )

    def in_running_state(
        self,
        *,
        time_mocking_ticks_granularity_fps: int = 60,  # i.e. when moving forward by 1 second we'll do it though 60 ticks
        waiting_duration_after_initialisation: float = 1,
        waiting_duration_after_yield: float = 0,
    ) -> AsyncContextManager[ClockMock]:
        async def run_app() -> None:
            await self.process_messages()

        @contextlib.asynccontextmanager
        async def get_running_state_context_manager():
            with mock_textual_timers(
                ticks_granularity_fps=time_mocking_ticks_granularity_fps
            ) as clock_mock:
                run_task = asyncio.create_task(run_app())

                # We have to do this because `run_app()` is running in its own async task, and our test is going to
                # run in this one - so the app must also be the active App in our current context:
                self._set_active()

                await clock_mock.advance_clock(waiting_duration_after_initialisation)
                # make sure the App has entered its main loop at this stage:
                assert self._driver is not None

                await self.force_full_screen_update()

                # And now it's time to pass the torch on to the test function!
                # We provide the `move_clock_forward` function to it,
                # so it can also do some time-based Textual stuff if it needs to:
                yield clock_mock

                await clock_mock.advance_clock(waiting_duration_after_yield)

                # Make sure our screen is up-to-date before exiting the context manager,
                # so tests using our `last_display_capture` for example can assert things on a fully refreshed screen:
                await self.force_full_screen_update()

            # End of simulated time: we just shut down ourselves:
            assert not run_task.done()
            await self.shutdown()

        return get_running_state_context_manager()

    async def boot_and_shutdown(
        self,
        *,
        waiting_duration_after_initialisation: float = 0.001,
        waiting_duration_before_shutdown: float = 0,
    ):
        """Just a commodity shortcut for `async with app.in_running_state(): pass`, for simple cases"""
        async with self.in_running_state(
            waiting_duration_after_initialisation=waiting_duration_after_initialisation,
            waiting_duration_after_yield=waiting_duration_before_shutdown,
        ):
            pass

    def get_char_at(self, x: int, y: int) -> str:
        """Get the character at the given cell or empty string

        Args:
            x (int): X position within the Layout
            y (int): Y position within the Layout

        Returns:
            str: The character at the cell (x, y) within the Layout
        """
        # N.B. Basically a copy-paste-and-slightly-adapt of `Compositor.get_style_at()`
        try:
            widget, region = self.get_widget_at(x, y)
        except errors.NoWidget:
            return ""
        if widget not in self.screen._compositor.regions:
            return ""

        x -= region.x
        y -= region.y
        lines = widget.render_lines(Region(0, y, region.width, 1))
        if not lines:
            return ""
        end = 0
        for segment in lines[0]:
            end += segment.cell_length
            if x < end:
                return segment.text[0]
        return ""

    async def force_full_screen_update(
        self, *, repaint: bool = True, layout: bool = True
    ) -> None:
        try:
            screen = self.screen
        except IndexError:
            return  # the app may not have a screen yet

        # We artificially tell the Compositor that the whole area should be refreshed
        screen._compositor._dirty_regions = {
            Region(0, 0, screen.size.width, screen.size.height),
        }
        screen.refresh(repaint=repaint, layout=layout)
        # We also have to make sure we have at least one dirty widget, or `screen._on_update()` will early return:
        screen._dirty_widgets.add(screen)
        screen._on_update()

        await let_asyncio_process_some_events()

    def on_exception(self, error: Exception) -> None:
        # In tests we want the errors to be raised, rather than printed to a Console
        raise error

    def run(self):
        raise NotImplementedError(
            "Use `async with my_test_app.in_running_state()` rather than `my_test_app.run()`"
        )

    @property
    def active_app(self) -> App | None:
        return active_app.get()

    @property
    def total_capture(self) -> str | None:
        return self.console.file.getvalue()

    @property
    def last_display_capture(self) -> str | None:
        total_capture = self.total_capture
        if not total_capture:
            return None
        screen_captures = total_capture.split(SYNC_START)
        for single_screen_capture in reversed(screen_captures):
            if len(single_screen_capture) > 30:
                # let's return the last occurrence of a screen that seem to be properly "fully-paint"
                return single_screen_capture
        return None

    @property
    def console(self) -> ConsoleTest:
        return self._console

    @console.setter
    def console(self, console: Console) -> None:
        """This is a no-op, the console is always a TestConsole"""
        return

    @property
    def error_console(self) -> ConsoleTest:
        return self._error_console

    @error_console.setter
    def error_console(self, console: Console) -> None:
        """This is a no-op, the error console is always a TestConsole"""
        return


class ConsoleTest(Console):
    def __init__(self, *, width: int, height: int):
        file = io.StringIO()
        super().__init__(
            color_system="256",
            file=file,
            width=width,
            height=height,
            force_terminal=False,
            legacy_windows=False,
        )

    @property
    def file(self) -> io.StringIO:
        return cast(io.StringIO, self._file)

    @property
    def is_dumb_terminal(self) -> bool:
        return False


class DriverTest(Driver):
    def start_application_mode(self) -> None:
        size = Size(self.console.size.width, self.console.size.height)
        event = events.Resize(self._target, size, size)
        asyncio.run_coroutine_threadsafe(
            self._target.post_message(event),
            loop=asyncio.get_running_loop(),
        )

    def disable_input(self) -> None:
        pass

    def stop_application_mode(self) -> None:
        pass


# It seems that we have to give _way more_ time to `asyncio` on Windows in order to see our different awaiters
# properly triggered when we pause our own "move clock forward" loop.
# It could be caused by the fact that the time resolution for `asyncio` on this platform seems rather low:
# > The resolution of the monotonic clock on Windows is usually around 15.6 msec.
# > The best resolution is 0.5 msec.
# @link https://docs.python.org/3/library/asyncio-platforms.html:
ASYNCIO_EVENTS_PROCESSING_REQUIRED_PERIOD = 0.025 if WINDOWS else 0.005


async def let_asyncio_process_some_events() -> None:
    await asyncio.sleep(ASYNCIO_EVENTS_PROCESSING_REQUIRED_PERIOD)


class ClockMock(_Clock):
    # To avoid issues with floats we will store the current time as an integer internally.
    # Tenths of microseconds should be a good enough granularity:
    TIME_RESOLUTION = 10_000_000

    def __init__(
        self,
        *,
        ticks_granularity_fps: int = 60,
    ):
        self._ticks_granularity_fps = ticks_granularity_fps
        self._single_tick_duration = int(self.TIME_RESOLUTION / ticks_granularity_fps)
        self._start_time: int = -1
        self._current_time: int = -1
        # For each call to our `sleep` method we will store an asyncio.Event
        # and the time at which we should trigger it:
        self._pending_sleep_events: dict[int, list[asyncio.Event]] = {}

    def get_time_no_wait(self) -> float:
        if self._current_time == -1:
            self._start_clock()

        return self._current_time / self.TIME_RESOLUTION

    async def sleep(self, seconds: float) -> None:
        event = asyncio.Event()
        internal_waiting_duration = int(seconds * self.TIME_RESOLUTION)
        target_event_monotonic_time = self._current_time + internal_waiting_duration
        self._pending_sleep_events.setdefault(target_event_monotonic_time, []).append(
            event
        )
        # Ok, let's wait for this Event
        # (which can only be "unlocked" by calls to `advance_clock()`)
        await event.wait()

    async def advance_clock(self, seconds: float) -> None:
        """
        Artificially advance the Textual clock forward.

        Args:
            seconds: for each second we will artificially tick `ticks_granularity_fps` times
        """
        if self._current_time == -1:
            self._start_clock()

        ticks_count = ceil(seconds * self._ticks_granularity_fps)
        activated_timers_count_total = 0  # useful when debugging this code :-)
        for tick_counter in range(ticks_count):
            self._current_time += self._single_tick_duration
            activated_timers_count = self._check_sleep_timers_to_activate()
            activated_timers_count_total += activated_timers_count
            # Now that we likely unlocked some occurrences of `await sleep(duration)`,
            # let's give an opportunity to asyncio-related stuff to happen:
            if activated_timers_count:
                await let_asyncio_process_some_events()

        await let_asyncio_process_some_events()

    def _start_clock(self) -> None:
        # N.B. `start_time` is not actually used, but it is useful to have when we set breakpoints there :-)
        self._start_time = self._current_time = int(monotonic() * self.TIME_RESOLUTION)

    def _check_sleep_timers_to_activate(self) -> int:
        activated_timers_count = 0
        activated_events_times_to_clear: list[int] = []
        for (monotonic_time, target_events) in self._pending_sleep_events.items():
            if self._current_time < monotonic_time:
                continue  # not time for you yet, dear awaiter...
            # Right, let's release these waiting events!
            for event in target_events:
                event.set()
            activated_timers_count += len(target_events)
            # ...and let's mark it for removal:
            activated_events_times_to_clear.append(monotonic_time)

        for event_time_to_clear in activated_events_times_to_clear:
            del self._pending_sleep_events[event_time_to_clear]

        return activated_timers_count


def mock_textual_timers(
    *,
    ticks_granularity_fps: int = 60,
) -> ContextManager[ClockMock]:
    @contextlib.contextmanager
    def mock_textual_timers_context_manager():
        clock_mock = ClockMock(ticks_granularity_fps=ticks_granularity_fps)
        with mock.patch("textual._clock._clock", new=clock_mock):
            yield clock_mock

    return mock_textual_timers_context_manager()
