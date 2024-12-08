from textual.app import App
from textual.command import CommandList, CommandPalette, Hit, Hits, Provider


class SimpleSource(Provider):
    async def search(self, query: str) -> Hits:
        def goes_nowhere_does_nothing() -> None:
            pass

        for _ in range(100):
            yield Hit(1, query, goes_nowhere_does_nothing, query)


class CommandPaletteApp(App[None]):
    COMMANDS = {SimpleSource}

    def on_mount(self) -> None:
        self.action_command_palette()


async def test_initial_list_no_highlight() -> None:
    """When the list initially appears, the first item is highlghted."""
    async with CommandPaletteApp().run_test() as pilot:
        assert CommandPalette.is_open(pilot.app)
        assert pilot.app.screen.query_one(CommandList).visible is False
        await pilot.press("a")
        assert pilot.app.screen.query_one(CommandList).visible is True
        assert pilot.app.screen.query_one(CommandList).highlighted == 0


async def test_down_arrow_selects_an_item() -> None:
    """Typing in a search value then pressing down should select a command."""
    async with CommandPaletteApp().run_test() as pilot:
        assert CommandPalette.is_open(pilot.app)
        assert pilot.app.screen.query_one(CommandList).visible is False
        await pilot.press("a")
        assert pilot.app.screen.query_one(CommandList).visible is True
        assert pilot.app.screen.query_one(CommandList).highlighted == 0
        await pilot.press("down")
        assert pilot.app.screen.query_one(CommandList).highlighted == 1


async def test_enter_selects_an_item() -> None:
    """Typing in a search value then pressing enter should dismiss the command palette."""
    async with CommandPaletteApp().run_test() as pilot:
        assert CommandPalette.is_open(pilot.app)
        assert pilot.app.screen.query_one(CommandList).visible is False
        await pilot.press("a")
        assert pilot.app.screen.query_one(CommandList).visible is True
        assert pilot.app.screen.query_one(CommandList).highlighted == 0
        await pilot.press("enter")
        assert not CommandPalette.is_open(pilot.app)
        assert not pilot.app.screen.query(CommandList)
