from __future__ import annotations

import asyncio
import contextlib
import io
from pathlib import Path
from time import monotonic
from typing import AsyncContextManager, cast, ContextManager, Callable
from unittest import mock

from rich.console import Console

from textual import events, errors
from textual._timer import Timer
from textual.app import App, ComposeResult
from textual.driver import Driver
from textual.geometry import Size


# N.B. These classes would better be named TestApp/TestConsole/TestDriver/etc,
# but it makes pytest emit warning as it will try to collect them as classes containing test cases :-/

# This value is also hard-coded in Textual's `App` class:
CLEAR_SCREEN_SEQUENCE = "\x1bP=1s\x1b\\"


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

        # We need this so the `CLEAR_SCREEN_SEQUENCE` is always sent for a screen refresh,
        # whatever the environment:
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
        waiting_duration_after_initialisation: float = 0.1,
        waiting_duration_post_yield: float = 0,
        time_acceleration: bool = True,
        time_acceleration_factor: float = 10,
        # force_timers_tick_after_yield: bool = True,
    ) -> AsyncContextManager:
        async def run_app() -> None:
            await self.process_messages()

        if time_acceleration:
            waiting_duration_after_initialisation /= time_acceleration_factor
            waiting_duration_post_yield /= time_acceleration_factor

        time_acceleration_context: ContextManager = (
            textual_timers_accelerate_time(acceleration_factor=time_acceleration_factor)
            if time_acceleration
            else contextlib.nullcontext()
        )

        @contextlib.asynccontextmanager
        async def get_running_state_context_manager():
            self._set_active()
            with time_acceleration_context:
                run_task = asyncio.create_task(run_app())
                timeout_before_yielding_task = asyncio.create_task(
                    asyncio.sleep(waiting_duration_after_initialisation)
                )
                done, pending = await asyncio.wait(
                    (
                        run_task,
                        timeout_before_yielding_task,
                    ),
                    return_when=asyncio.FIRST_COMPLETED,
                )
                if run_task in done or run_task not in pending:
                    raise RuntimeError(
                        "TestApp is no longer running after its initialization period"
                    )
                yield
                waiting_duration = max(
                    waiting_duration_post_yield or 0,
                    self.screen._update_timer._interval,
                )
                await asyncio.sleep(waiting_duration)
                # if force_timers_tick_after_yield:
                #     await textual_timers_force_tick()
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
            waiting_duration_post_yield=waiting_duration_before_shutdown,
        ):
            pass

    def run(self):
        raise NotImplementedError(
            "Use `async with my_test_app.in_running_state()` rather than `my_test_app.run()`"
        )

    @property
    def total_capture(self) -> str | None:
        return self.console.file.getvalue()

    @property
    def last_display_capture(self) -> str | None:
        total_capture = self.total_capture
        if not total_capture:
            return None
        last_display_start_index = total_capture.rindex(CLEAR_SCREEN_SEQUENCE)
        return total_capture[last_display_start_index:]

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
        lines = widget.get_render_lines(y, y + 1)
        if not lines:
            return ""
        end = 0
        for segment in lines[0]:
            end += segment.cell_length
            if x < end:
                return segment.text[0]
        return ""

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


async def textual_timers_force_tick() -> None:
    timer_instances_tick_tasks: list[asyncio.Task] = []
    for timer in Timer._instances:
        task = asyncio.create_task(timer._tick(next_timer=0, count=0))
        timer_instances_tick_tasks.append(task)
    await asyncio.wait(timer_instances_tick_tasks)


def textual_timers_accelerate_time(
    *, acceleration_factor: float = 10
) -> ContextManager:
    @contextlib.contextmanager
    def accelerate_time_for_timer_context_manager():
        starting_time = monotonic()

        # Our replacement for "textual._timer.Timer._sleep":
        async def timer_sleep(duration: float) -> None:
            await asyncio.sleep(duration / acceleration_factor)

        # Our replacement for "textual._timer.Timer.get_time":
        def timer_get_time() -> float:
            real_now = monotonic()
            real_elapsed_time = real_now - starting_time
            accelerated_elapsed_time = real_elapsed_time * acceleration_factor
            print(
                f"timer_get_time:: accelerated_elapsed_time={accelerated_elapsed_time}"
            )
            return starting_time + accelerated_elapsed_time

        with mock.patch("textual._timer.Timer._sleep") as timer_sleep_mock, mock.patch(
            "textual._timer.Timer.get_time"
        ) as timer_get_time_mock, mock.patch(
            "textual.message.Message._get_time"
        ) as message_get_time_mock:
            timer_sleep_mock.side_effect = timer_sleep
            timer_get_time_mock.side_effect = timer_get_time
            message_get_time_mock.side_effect = timer_get_time
            yield

    return accelerate_time_for_timer_context_manager()
