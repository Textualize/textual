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
        assert len(pilot.app.query(CommandPalette)) == 1
        await pilot.press("escape")
        assert len(pilot.app.query(CommandPalette)) == 0


async def test_escape_does_not_close_when_list_visible() -> None:
    """Pressing escape when a hit list is visible should not close the command palette."""
    async with CommandPaletteApp().run_test() as pilot:
        assert len(pilot.app.query(CommandPalette)) == 1
        await pilot.press("a")
        await pilot.press("escape")
        assert len(pilot.app.query(CommandPalette)) == 1
        await pilot.press("escape")
        assert len(pilot.app.query(CommandPalette)) == 0


async def test_down_arrow_should_undo_closing_of_list_via_escape() -> None:
    """Down arrow should reopen the hit list if escape closed it before."""
    async with CommandPaletteApp().run_test() as pilot:
        assert len(pilot.app.query(CommandPalette)) == 1
        await pilot.press("a")
        await pilot.press("escape")
        assert len(pilot.app.query(CommandPalette)) == 1
        await pilot.press("down")
        await pilot.press("escape")
        assert len(pilot.app.query(CommandPalette)) == 1
        await pilot.press("escape")
        assert len(pilot.app.query(CommandPalette)) == 0
