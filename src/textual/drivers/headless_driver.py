from __future__ import annotations

from ..driver import Driver
from ..geometry import Size
from .. import events


class HeadlessDriver(Driver):
    """A do-nothing driver for testing."""

    @property
    def is_headless(self) -> bool:
        return True

    def _get_terminal_size(self) -> tuple[int, int]:
        if self._size is not None:
            return self._size
        width: int | None = 80
        height: int | None = 25
        import shutil

        try:
            width, height = shutil.get_terminal_size()
        except (AttributeError, ValueError, OSError):
            try:
                width, height = shutil.get_terminal_size()
            except (AttributeError, ValueError, OSError):
                pass
        width = width or 80
        height = height or 25
        return width, height

    async def start_application_mode(self) -> None:
        async def send_size_event():
            terminal_size = self._get_terminal_size()
            width, height = terminal_size
            textual_size = Size(width, height)
            event = events.Resize(self._target, textual_size, textual_size)
            await self._target.post_message(event)

        await send_size_event()

    async def disable_input(self) -> None:
        pass

    def stop_application_mode(self) -> None:
        pass
