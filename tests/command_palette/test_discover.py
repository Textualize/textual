from textual.app import App
from textual.command import CommandPalette, DiscoveryHit, Hit, Hits, Provider
from textual.widgets import OptionList


class SimpleSource(Provider):

    async def discover(self) -> Hits:
        def goes_nowhere_does_nothing() -> None:
            pass

        yield DiscoveryHit("XD-1", goes_nowhere_does_nothing, "XD-1")

    async def search(self, query: str) -> Hits:
        def goes_nowhere_does_nothing() -> None:
            pass

        yield Hit(1, query, goes_nowhere_does_nothing, query)


class CommandPaletteApp(App[None]):
    COMMANDS = {SimpleSource}

    def on_mount(self) -> None:
        self.action_command_palette()


async def test_discovery_visible() -> None:
    """A provider with discovery should cause the command palette to be opened right away."""
    async with CommandPaletteApp().run_test() as pilot:
        assert CommandPalette.is_open(pilot.app)
        results = pilot.app.screen.query_one(OptionList)
        assert results.visible is True
        assert results.option_count == 1
