from __future__ import annotations

import asyncio

from textual import events
from textual.driver import Driver
from textual.geometry import Size


class HeadlessDriver(Driver):
    """A do-nothing driver for testing."""

    @property
    def is_headless(self) -> bool:
        """Is the driver running in 'headless' mode?"""
        return True

    def _get_terminal_size(self) -> tuple[int, int]:
        if self._size is not None:
            return self._size
        try:
            width = int(os.environ['COLUMNS'])
        except (KeyError, ValueError):
            width: int | None = 0

        try:
            height = int(os.environ['LINES'])
        except (KeyError, ValueError):
            height: int | None = 0

        if width <= 0 or height <= 0:
            try:
                width, height = os.get_terminal_size(self._file.fileno())
            except (AttributeError, ValueError, OSError):
                try:
                    width, height = os.get_terminal_size(self._file.fileno())
                except (AttributeError, ValueError, OSError):
                    pass
            width = width or 80
            height = height or 25
        return width, height

    def write(self, data: str) -> None:
        """Write data to the output device.

        Args:
            data: Raw data.
        """
        # Nothing to write as this is a headless driver.

    def start_application_mode(self) -> None:
        """Start application mode."""
        loop = asyncio.get_running_loop()

        def send_size_event() -> None:
            """Send first resize event."""
            terminal_size = self._get_terminal_size()
            width, height = terminal_size
            textual_size = Size(width, height)
            event = events.Resize(textual_size, textual_size)
            asyncio.run_coroutine_threadsafe(
                self._app._post_message(event),
                loop=loop,
            )

        send_size_event()

    def disable_input(self) -> None:
        """Disable further input."""

    def stop_application_mode(self) -> None:
        """Stop application mode, restore state."""
        # Nothing to do
