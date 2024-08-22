from typing import Iterable

from textual.app import App, SystemCommand
from textual.screen import Screen


class BellCommandApp(App):
    """An app with a 'bell' command."""

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)  # (1)!
        yield SystemCommand("Bell", "Ring the bell", self.bell)  # (2)!


if __name__ == "__main__":
    app = BellCommandApp()
    app.run()
