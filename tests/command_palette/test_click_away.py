from textual.app import App
from textual.command_palette import (
    CommandMatches,
    CommandPalette,
    CommandSource,
    CommandSourceHit,
)


class SimpleSource(CommandSource):
    async def search_for(self, user_input: str) -> CommandMatches:
        def gndn() -> None:
            pass

        yield CommandSourceHit(1, user_input, gndn, user_input)


class CommandPaletteApp(App[None]):
    def on_mount(self) -> None:
        self.action_command_palette()


async def test_clicking_outside_command_palette_closes_it() -> None:
    """Clicking 'outside' the command palette should make it go away."""
    async with CommandPaletteApp().run_test() as pilot:
        assert len(pilot.app.query(CommandPalette)) == 1
        await pilot.click()
        assert len(pilot.app.query(CommandPalette)) == 0
