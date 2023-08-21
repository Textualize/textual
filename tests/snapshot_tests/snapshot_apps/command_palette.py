from textual.app import App
from textual.command_palette import CommandSource, CommandMatches, CommandSourceHit

class TestSource(CommandSource):

    def gndn(self) -> None:
        pass

    async def hunt_for(self, user_input: str) -> CommandMatches:
        matcher = self.matcher(user_input)
        for n in range(10):
            command = f"This is a test of this code {n}"
            yield CommandSourceHit(
                n/10, matcher.highlight(command), self.gndn, command
            )

class CommandPaletteApp(App[None]):

    COMMAND_SOURCES = {TestSource}

    def on_mount(self) -> None:
        self.action_command_palette()

if __name__ == "__main__":
    CommandPaletteApp().run()
