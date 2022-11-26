from contextlib import contextmanager
from typing import Generator
import anyio
import sniffio


class Flag:
    def __init__(self):
        self._event = anyio.Event()

    def set(self) -> None:
        self._event.set()

    def clear(self) -> None:
        if self._event.is_set():
            self._event = anyio.Event()

    async def wait(self) -> None:
        await self._event.wait()


@contextmanager
def _spoof_asyncio_if_needed() -> Generator[str, None, None]:
    """
    A context manager that ensures anyio has an async library set, forcing
    asyncio if we are not running in an async context.

    Returns:
        str: The flavor of async library that is in use.
    """
    try:
        current_lib = sniffio.current_async_library()
        reset_token = None
    except sniffio.AsyncLibraryNotFoundError:
        current_lib = "asyncio"
        reset_token = sniffio.current_async_library_cvar.set("asyncio")

    try:
        yield current_lib
    finally:
        if reset_token is not None:
            sniffio.current_async_library_cvar.reset(reset_token)
