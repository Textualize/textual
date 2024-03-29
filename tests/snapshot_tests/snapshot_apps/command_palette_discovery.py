from textual.app import App
from textual.command import DiscoveryHit, Hit, Hits, Provider


class TestSource(Provider):
    def goes_nowhere_does_nothing(self) -> None:
        pass

    async def discover(self) -> Hits:
        for n in range(10):
            command = f"This is a test of this code {n}"
            yield DiscoveryHit(
                command,
                self.goes_nowhere_does_nothing,
                command,
            )

    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)
        for n in range(10):
            command = f"This should not appear {n}"
            yield Hit(
                n / 10,
                matcher.highlight(command),
                self.goes_nowhere_does_nothing,
                command,
            )


class CommandPaletteApp(App[None]):
    COMMANDS = {TestSource}

    def on_mount(self) -> None:
        self.action_command_palette()


if __name__ == "__main__":
    CommandPaletteApp().run()
