from textual.app import App
from textual.command import CommandPalette, Hit, Hits, Source


class SimpleSource(Source):
    async def search(self, query: str) -> Hits:
        def goes_nowhere_does_nothing() -> None:
            pass

        yield Hit(1, query, goes_nowhere_does_nothing, query)


class CommandPaletteApp(App[None]):
    COMMAND_SOURCES = {SimpleSource}

    def on_mount(self) -> None:
        self.action_command_palette()


async def test_clicking_outside_command_palette_closes_it() -> None:
    """Clicking 'outside' the command palette should make it go away."""
    async with CommandPaletteApp().run_test() as pilot:
        assert len(pilot.app.query(CommandPalette)) == 1
        await pilot.click()
        assert len(pilot.app.query(CommandPalette)) == 0
