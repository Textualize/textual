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


async def test_clicking_outside_command_palette_closes_it() -> None:
    """Clicking 'outside' the command palette should make it go away."""
    async with CommandPaletteApp().run_test() as pilot:
        assert isinstance(pilot.app.screen, CommandPalette)
        await pilot.click()
        assert not isinstance(pilot.app.screen, CommandPalette)
