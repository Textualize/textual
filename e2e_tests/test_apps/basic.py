from pathlib import Path

from rich.console import RenderableType
from rich.style import Style
from rich.syntax import Syntax
from rich.text import Text

from textual.app import App
from textual.widget import Widget
from textual.widgets import Static

CODE = '''
class Offset(NamedTuple):
    """A point defined by x and y coordinates."""

    x: int = 0
    y: int = 0

    @property
    def is_origin(self) -> bool:
        """Check if the point is at the origin (0, 0)"""
        return self == (0, 0)

    def __bool__(self) -> bool:
        return self != (0, 0)

    def __add__(self, other: object) -> Offset:
        if isinstance(other, tuple):
            _x, _y = self
            x, y = other
            return Offset(_x + x, _y + y)
        return NotImplemented

    def __sub__(self, other: object) -> Offset:
        if isinstance(other, tuple):
            _x, _y = self
            x, y = other
            return Offset(_x - x, _y - y)
        return NotImplemented

    def __mul__(self, other: object) -> Offset:
        if isinstance(other, (float, int)):
            x, y = self
            return Offset(int(x * other), int(y * other))
        return NotImplemented
'''


lorem = Text.from_markup(
    """Lorem ipsum dolor sit amet, consectetur adipiscing elit. In velit libero, volutpat nec hendrerit at, faucibus in odio. Aliquam hendrerit nibh sed quam volutpat maximus. Nullam suscipit convallis lorem quis sodales. In tristique lobortis ante et dictum. Ut at finibus ipsum. In urna dolor, placerat et mi facilisis, congue sollicitudin massa. Phasellus felis turpis, cursus eu lectus et, porttitor malesuada augue. Sed feugiat volutpat velit, sollicitudin fringilla velit bibendum faucibus. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In velit libero, volutpat nec hendrerit at, faucibus in odio. Aliquam hendrerit nibh sed quam volutpat maximus. Nullam suscipit convallis lorem quis sodales. In tristique lobortis ante et dictum. Ut at finibus ipsum. In urna dolor, placerat et mi facilisis, congue sollicitudin massa. Phasellus felis turpis, cursus eu lectus et, porttitor malesuada augue. Sed feugiat volutpat velit, sollicitudin fringilla velit bibendum faucibus. """
    """Lorem ipsum dolor sit amet, consectetur adipiscing elit. In velit libero, volutpat nec hendrerit at, faucibus in odio. Aliquam hendrerit nibh sed quam volutpat maximus. Nullam suscipit convallis lorem quis sodales. In tristique lobortis ante et dictum. Ut at finibus ipsum. In urna dolor, placerat et mi facilisis, congue sollicitudin massa. Phasellus felis turpis, cursus eu lectus et, porttitor malesuada augue. Sed feugiat volutpat velit, sollicitudin fringilla velit bibendum faucibus. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In velit libero, volutpat nec hendrerit at, faucibus in odio. Aliquam hendrerit nibh sed quam volutpat maximus. Nullam suscipit convallis lorem quis sodales. In tristique lobortis ante et dictum. Ut at finibus ipsum. In urna dolor, placerat et mi facilisis, congue sollicitudin massa. Phasellus felis turpis, cursus eu lectus et, porttitor malesuada augue. Sed feugiat volutpat velit, sollicitudin fringilla velit bibendum faucibus. """
)


class TweetHeader(Widget):
    def render(self) -> RenderableType:
        return Text("Lorem Impsum", justify="center")


class TweetBody(Widget):
    def render(self) -> Text:
        return lorem


class Tweet(Widget):
    pass


class OptionItem(Widget):
    def render(self) -> Text:
        return Text("Option")


class Error(Widget):
    def render(self) -> Text:
        return Text("This is an error message", justify="center")


class Warning(Widget):
    def render(self) -> Text:
        return Text("This is a warning message", justify="center")


class Success(Widget):
    def render(self) -> Text:
        return Text("This is a success message", justify="center")


class BasicApp(App):
    """A basic app demonstrating CSS"""

    def on_load(self):
        """Bind keys here."""
        self.bind("tab", "toggle_class('#sidebar', '-active')")

    def on_mount(self):
        """Build layout here."""
        self.mount(
            header=Static(
                Text.from_markup(
                    "[b]This is a [u]Textual[/u] app, running in the terminal"
                ),
            ),
            content=Widget(
                Tweet(
                    TweetBody(),
                    # Widget(
                    #     Widget(classes={"button"}),
                    #     Widget(classes={"button"}),
                    #     classes={"horizontal"},
                    # ),
                ),
                Widget(
                    Static(Syntax(CODE, "python"), classes="code"),
                    classes="scrollable",
                ),
                Error(),
                Tweet(TweetBody()),
                Warning(),
                Tweet(TweetBody()),
                Success(),
            ),
            footer=Widget(),
            sidebar=Widget(
                Widget(classes="title"),
                Widget(classes="user"),
                OptionItem(),
                OptionItem(),
                OptionItem(),
                Widget(classes="content"),
            ),
        )

    async def on_key(self, event) -> None:
        await self.dispatch_key(event)

    def key_d(self):
        self.dark = not self.dark

    def key_x(self):
        self.panic(self.tree)


sandbox_folder = Path(__file__).parent
app = BasicApp(
    css_path=sandbox_folder / "basic.css",
    watch_css=True,
    log_path=sandbox_folder / "basic.log",
    log_verbosity=0,
)

if __name__ == "__main__":
    app.run()
