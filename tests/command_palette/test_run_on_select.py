from functools import partial

from textual.app import App
from textual.command_palette import (
    CommandMatches,
    CommandPalette,
    CommandSource,
    CommandSourceHit,
)
from textual.widgets import Input


class SimpleSource(CommandSource):
    async def search_for(self, _: str) -> CommandMatches:
        def gndn(selection: int) -> None:
            assert isinstance(self.app, CommandPaletteRunOnSelectApp)
            self.app.selection = selection

        for n in range(100):
            yield CommandSourceHit(
                n + 1 / 100, str(n), partial(gndn, n), str(n), f"This is help for {n}"
            )


class CommandPaletteRunOnSelectApp(App[None]):
    COMMAND_SOURCES = {SimpleSource}

    def __init__(self) -> None:
        super().__init__()
        self.selection: int | None = None


async def test_with_run_on_select_on() -> None:
    """With run on select on, the callable should be instantly run."""
    async with CommandPaletteRunOnSelectApp().run_test() as pilot:
        save = CommandPalette.run_on_select
        CommandPalette.run_on_select = True
        assert isinstance(pilot.app, CommandPaletteRunOnSelectApp)
        pilot.app.action_command_palette()
        await pilot.press("0")
        await pilot.app.query_one(CommandPalette).workers.wait_for_complete()
        await pilot.press("down")
        await pilot.press("enter")
        assert pilot.app.selection is not None
        CommandPalette.run_on_select = save


class CommandPaletteDoNotRunOnSelectApp(CommandPaletteRunOnSelectApp):
    def __init__(self) -> None:
        super().__init__()


async def test_with_run_on_select_off() -> None:
    """With run on select off, the callable should not be instantly run."""
    async with CommandPaletteDoNotRunOnSelectApp().run_test() as pilot:
        save = CommandPalette.run_on_select
        CommandPalette.run_on_select = False
        assert isinstance(pilot.app, CommandPaletteDoNotRunOnSelectApp)
        pilot.app.action_command_palette()
        await pilot.press("0")
        await pilot.app.query_one(CommandPalette).workers.wait_for_complete()
        await pilot.press("down")
        await pilot.press("enter")
        assert pilot.app.selection is None
        assert pilot.app.query_one(Input).value != ""
        await pilot.press("enter")
        assert pilot.app.selection is not None
        CommandPalette.run_on_select = save
