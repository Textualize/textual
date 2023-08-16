from textual.app import App
from textual.command_palette import (
    CommandList,
    CommandMatches,
    CommandPalette,
    CommandSource,
    CommandSourceHit,
)


class SimpleSource(CommandSource):
    async def hunt_for(self, user_input: str) -> CommandMatches:
        def gndn() -> None:
            pass

        for _ in range(100):
            yield CommandSourceHit(1, user_input, gndn, user_input)


class CommandPaletteApp(App[None]):
    def on_mount(self) -> None:
        self.action_command_palette()


async def test_initial_list_no_highlight() -> None:
    """When the list initially appears, nothing will be highlighted."""
    async with CommandPaletteApp().run_test() as pilot:
        assert len(pilot.app.query(CommandPalette)) == 1
        assert pilot.app.query_one(CommandList).visible is False
        await pilot.press("a")
        assert pilot.app.query_one(CommandList).visible is True
        assert pilot.app.query_one(CommandList).highlighted is None


async def test_down_arrow_selects_an_item() -> None:
    """Typing in a search value then pressing down should select a command."""
    async with CommandPaletteApp().run_test() as pilot:
        assert len(pilot.app.query(CommandPalette)) == 1
        assert pilot.app.query_one(CommandList).visible is False
        await pilot.press("a")
        assert pilot.app.query_one(CommandList).visible is True
        assert pilot.app.query_one(CommandList).highlighted is None
        await pilot.press("down")
        assert pilot.app.query_one(CommandList).highlighted is not None


async def test_enter_selects_an_item() -> None:
    """Typing in a search value then pressing enter should select a command."""
    async with CommandPaletteApp().run_test() as pilot:
        assert len(pilot.app.query(CommandPalette)) == 1
        assert pilot.app.query_one(CommandList).visible is False
        await pilot.press("a")
        assert pilot.app.query_one(CommandList).visible is True
        assert pilot.app.query_one(CommandList).highlighted is None
        await pilot.press("enter")
        assert pilot.app.query_one(CommandList).highlighted is not None


async def test_selection_of_command_closes_command_palette() -> None:
    """Selecting a command from the list should close the list."""
    async with CommandPaletteApp().run_test() as pilot:
        assert len(pilot.app.query(CommandPalette)) == 1
        assert pilot.app.query_one(CommandList).visible is False
        await pilot.press("a")
        assert pilot.app.query_one(CommandList).visible is True
        assert pilot.app.query_one(CommandList).highlighted is None
        await pilot.press("enter")
        assert pilot.app.query_one(CommandList).highlighted is not None
        await pilot.press("enter")
        assert len(pilot.app.query(CommandPalette)) == 0
