from __future__ import annotations

from textual.app import App, ComposeResult
from textual.command import Hit, Hits, Provider
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Input


class SimpleSource(Provider):
    environment: set[tuple[App, Screen, Widget | None]] = set()

    async def search(self, _: str) -> Hits:
        def goes_nowhere_does_nothing() -> None:
            pass

        SimpleSource.environment.add((self.app, self.screen, self.focused))
        yield Hit(1, "Hit", goes_nowhere_does_nothing, "Hit")


class CommandPaletteApp(App[None]):
    COMMANDS = {SimpleSource}

    def compose(self) -> ComposeResult:
        yield Input()

    def on_mount(self) -> None:
        self.action_command_palette()


async def test_command_source_environment() -> None:
    """The command source should see the app and default screen."""
    async with CommandPaletteApp().run_test() as pilot:
        base_screen, *_ = pilot.app.children
        assert base_screen is not None
        await pilot.press(*"test")
        assert len(SimpleSource.environment) == 1
        assert SimpleSource.environment == {
            (pilot.app, base_screen, base_screen.query_one(Input))
        }
