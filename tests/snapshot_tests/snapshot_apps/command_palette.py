from textual.app import App
from textual.command_palette import CommandSource, CommandMatches, CommandSourceHit

class TestSource(CommandSource):

    def goes_nowhere_does_nothing(self) -> None:
        pass

    async def search(self, query: str) -> CommandMatches:
        matcher = self.matcher(query)
        for n in range(10):
            command = f"This is a test of this code {n}"
            yield CommandSourceHit(
                n/10, matcher.highlight(command), self.goes_nowhere_does_nothing, command
            )

class CommandPaletteApp(App[None]):

    COMMAND_SOURCES = {TestSource}

    def on_mount(self) -> None:
        self.action_command_palette()

if __name__ == "__main__":
    CommandPaletteApp().run()
