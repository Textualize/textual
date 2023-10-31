"""Tests for https://github.com/Textualize/textual/issues/3615"""

from asyncio import sleep

from textual import work
from textual.app import App
from textual.command import Hit, Hits, Provider


class SimpleSource(Provider):
    async def search(self, query: str) -> Hits:
        def goes_nowhere_does_nothing() -> None:
            pass

        for _ in range(100):
            yield Hit(1, query, goes_nowhere_does_nothing, query)


class CommandPaletteApp(App[None]):
    COMMANDS = {SimpleSource}

    def on_mount(self) -> None:
        self.innocent_worker()

    @work
    async def innocent_worker(self) -> None:
        while True:
            await sleep(1)


async def test_innocent_worker_is_untouched() -> None:
    """Using the command palette should not halt other workers."""
    async with CommandPaletteApp().run_test() as pilot:
        assert len(pilot.app.workers) > 0
        pilot.app.action_command_palette()
        await pilot.press("a", "enter")
        assert len(pilot.app.workers) > 0
