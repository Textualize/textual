from typing import Union
from unittest import mock

from textual import on
from textual.app import App
from textual.command import CommandPalette, Hit, Hits, Provider

CommandPaletteEvent = Union[
    CommandPalette.Opened, CommandPalette.Closed, CommandPalette.OptionHighlighted
]


class SimpleSource(Provider):
    async def search(self, query: str) -> Hits:
        def goes_nowhere_does_nothing() -> None:
            pass

        yield Hit(1, query, goes_nowhere_does_nothing, query)


class AppWithActiveCommandPalette(App[None]):
    COMMANDS = {SimpleSource}

    def __init__(self) -> None:
        super().__init__()
        self.events: list[CommandPaletteEvent] = []

    def on_mount(self) -> None:
        self.action_command_palette()

    @on(CommandPalette.Opened)
    @on(CommandPalette.Closed)
    @on(CommandPalette.OptionHighlighted)
    def record_event(
        self,
        event: CommandPaletteEvent,
    ) -> None:
        self.events.append(event)


async def test_command_palette_opened_event():
    app = AppWithActiveCommandPalette()
    async with app.run_test():
        assert app.events == [CommandPalette.Opened()]


async def test_command_palette_closed_event():
    app = AppWithActiveCommandPalette()
    async with app.run_test() as pilot:
        await pilot.press("escape")
        assert app.events == [CommandPalette.Opened(), CommandPalette.Closed(False)]


async def test_command_palette_closed_event_value():
    app = AppWithActiveCommandPalette()
    async with app.run_test() as pilot:
        await pilot.press("a")
        await pilot.press("down")
        await pilot.press("enter")
        assert app.events == [
            CommandPalette.Opened(),
            CommandPalette.OptionHighlighted(mock.ANY),
            CommandPalette.Closed(True),
        ]


async def test_command_palette_option_highlighted_event():
    app = AppWithActiveCommandPalette()
    async with app.run_test() as pilot:
        await pilot.press("a")
        await pilot.press("down")
        assert app.events == [
            CommandPalette.Opened(),
            CommandPalette.OptionHighlighted(mock.ANY),
        ]
