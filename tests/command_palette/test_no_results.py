from textual.app import App
from textual.command import CommandPalette
from textual.widgets import OptionList


class CommandPaletteApp(App[None]):
    COMMANDS = set()

    def on_mount(self) -> None:
        self.action_command_palette()


async def test_no_results() -> None:
    """Receiving no results from a search for a command should not be a problem."""
    async with CommandPaletteApp().run_test() as pilot:
        assert CommandPalette.is_open(pilot.app)
        results = pilot.app.screen.query_one(OptionList)
        assert results.visible is False
        assert results.option_count == 0
        await pilot.press("a")
        # https://github.com/Textualize/textual/issues/3700 -- note the
        # little bit of wiggle room to allow for Windows.
        await pilot.pause(delay=CommandPalette._NO_MATCHES_COUNTDOWN + 0.1)
        assert results.visible is True
        assert results.option_count == 1
        assert "No matches found" in str(results.get_option_at_index(0).prompt)
        assert results.get_option_at_index(0).disabled is True
