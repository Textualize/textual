from __future__ import annotations

import asyncio
import contextlib
import io
from pathlib import Path
from typing import AsyncContextManager, cast

from rich.console import Console

from textual import events
from textual.app import App, ReturnType, ComposeResult
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
    ) -> AsyncContextManager:
        async def run_app() -> None:
            await self.process_messages()

        @contextlib.asynccontextmanager
        async def get_running_state_context_manager():
            self._set_active()
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
            if waiting_duration_post_yield:
                await asyncio.sleep(waiting_duration_post_yield)
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
