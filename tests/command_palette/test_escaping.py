from textual.app import App
from textual.command import CommandPalette, Hit, Hits, Provider


class SimpleSource(Provider):
    async def search(self, query: str) -> Hits:
        def goes_nowhere_does_nothing() -> None:
            pass

        yield Hit(1, query, goes_nowhere_does_nothing, query)


class CommandPaletteApp(App[None]):
    COMMANDS = {SimpleSource}

    def on_mount(self) -> None:
        self.action_command_palette()


async def test_escape_closes_when_no_list_visible() -> None:
    """Pressing escape when no list is visible should close the command palette."""
    async with CommandPaletteApp().run_test() as pilot:
        assert CommandPalette.is_open(pilot.app)
        await pilot.press("escape")
        assert not CommandPalette.is_open(pilot.app)
