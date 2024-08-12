from dataclasses import dataclass
from functools import partial

from textual import on
from textual._color_constants import COLOR_NAME_TO_RGB
from textual.app import App, ComposeResult
from textual.command import Hit, Hits, Provider
from textual.message import Message
from textual.widgets import Header, Static


@dataclass
class SwitchColor(Message, bubble=False):
    """Message to tell the app to switch color."""

    color: str


class ColorCommands(Provider):
    """A command provider to select colors."""

    async def search(self, query: str) -> Hits:
        """Called for each key."""
        matcher = self.matcher(query)
        for color in COLOR_NAME_TO_RGB.keys():
            score = matcher.match(color)
            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(color),
                    partial(self.app.post_message, SwitchColor(color)),
                )


class ColorBlock(Static):
    """Simple block of color."""

    DEFAULT_CSS = """
    ColorBlock{
        padding: 3 6;
        margin: 1 2;
        color: auto;
    }
    """


class ColorApp(App):
    """Experiment with the command palette."""

    COMMANDS = App.COMMANDS | {ColorCommands}
    TITLE = "Press ctrl + p and type a color"

    def compose(self) -> ComposeResult:
        yield Header()

    @on(SwitchColor)
    def switch_color(self, event: SwitchColor) -> None:
        """Adds a color block on demand."""
        color_block = ColorBlock(event.color)
        color_block.styles.background = event.color
        self.mount(color_block)
        self.screen.scroll_end()


if __name__ == "__main__":
    app = ColorApp()
    app.run()
