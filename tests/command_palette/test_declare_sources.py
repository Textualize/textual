from textual.app import App
from textual.command import CommandPalette, Hit, Hits, Source
from textual.screen import Screen


async def test_sources_with_no_known_screen() -> None:
    """A command palette with no known screen should have an empty source set."""
    assert CommandPalette()._source_classes == set()


class ExampleCommandSource(Source):
    async def search(self, _: str) -> Hits:
        def goes_nowhere_does_nothing() -> None:
            pass

        yield Hit(1, "Hit", goes_nowhere_does_nothing, "Hit")


class AppWithActiveCommandPalette(App[None]):
    def on_mount(self) -> None:
        self.action_command_palette()


class AppWithNoSources(AppWithActiveCommandPalette):
    pass


async def test_no_app_command_sources() -> None:
    """An app with no sources declared should work fine."""
    async with AppWithNoSources().run_test() as pilot:
        assert (
            pilot.app.query_one(CommandPalette)._source_classes == App.COMMAND_SOURCES
        )


class AppWithSources(AppWithActiveCommandPalette):
    COMMAND_SOURCES = {ExampleCommandSource}


async def test_app_command_sources() -> None:
    """Command sources declared on an app should be in the command palette."""
    async with AppWithSources().run_test() as pilot:
        assert (
            pilot.app.query_one(CommandPalette)._source_classes
            == AppWithSources.COMMAND_SOURCES
        )


class AppWithInitialScreen(App[None]):
    def __init__(self, screen: Screen) -> None:
        super().__init__()
        self._test_screen = screen

    def on_mount(self) -> None:
        self.push_screen(self._test_screen)


class ScreenWithNoSources(Screen[None]):
    def on_mount(self) -> None:
        self.app.action_command_palette()


async def test_no_screen_command_sources() -> None:
    """An app with a screen with no sources declared should work fine."""
    async with AppWithInitialScreen(ScreenWithNoSources()).run_test() as pilot:
        assert (
            pilot.app.query_one(CommandPalette)._source_classes == App.COMMAND_SOURCES
        )


class ScreenWithSources(ScreenWithNoSources):
    COMMAND_SOURCES = {ExampleCommandSource}


async def test_screen_command_sources() -> None:
    """Command sources declared on a screen should be in the command palette."""
    async with AppWithInitialScreen(ScreenWithSources()).run_test() as pilot:
        assert (
            pilot.app.query_one(CommandPalette)._source_classes
            == App.COMMAND_SOURCES | ScreenWithSources.COMMAND_SOURCES
        )


class AnotherCommandSource(ExampleCommandSource):
    pass


class CombinedSourceApp(App[None]):
    COMMAND_SOURCES = {AnotherCommandSource}

    def on_mount(self) -> None:
        self.push_screen(ScreenWithSources())


async def test_app_and_screen_command_sources_combine() -> None:
    """If an app and the screen have command sources they should combine."""
    async with CombinedSourceApp().run_test() as pilot:
        assert (
            pilot.app.query_one(CommandPalette)._source_classes
            == CombinedSourceApp.COMMAND_SOURCES | ScreenWithSources.COMMAND_SOURCES
        )
