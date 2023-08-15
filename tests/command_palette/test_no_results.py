from textual.app import App
from textual.command_palette import (
    CommandMatches,
    CommandPalette,
    CommandSource,
    CommandSourceHit,
)
from textual.widgets import OptionList


class SimpleSource(CommandSource):
    async def hunt_for(self, user_input: str) -> CommandMatches:
        def gndn() -> None:
            pass

        if user_input == "this will never happen in this test":
            yield CommandSourceHit(1, user_input, gndn, user_input)


class CommandPaletteApp(App[None]):
    COMMAND_SOURCES = {SimpleSource}

    def on_mount(self) -> None:
        self.action_command_palette()


async def test_no_results() -> None:
    """Receiving no results from a hunt for a command should not be a problem."""
    async with CommandPaletteApp().run_test() as pilot:
        assert len(pilot.app.query(CommandPalette)) == 1
        results = pilot.app.screen.query_one(OptionList)
        assert results.visible is False
        assert results.option_count == 0
        await pilot.press("a")
        await pilot.pause()
        assert results.visible is True
        assert results.option_count == 1
        assert "No matches found" in str(results.get_option_at_index(0).prompt)
        assert results.get_option_at_index(0).disabled is True
