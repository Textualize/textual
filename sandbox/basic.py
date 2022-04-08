from rich.align import Align
from rich.console import RenderableType
from rich.text import Text

from textual.app import App
from textual.widget import Widget


lorem = Text.from_markup(
    """Lorem ipsum dolor sit amet, consectetur adipiscing elit. In velit libero, volutpat nec hendrerit at, faucibus in odio. Aliquam hendrerit nibh sed quam volutpat maximus. Nullam suscipit convallis lorem quis sodales. In tristique lobortis ante et dictum. Ut at finibus ipsum. In urna dolor, placerat et mi facilisis, congue sollicitudin massa. Phasellus felis turpis, cursus eu lectus et, porttitor malesuada augue. Sed feugiat volutpat velit, sollicitudin fringilla velit bibendum faucibus. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In velit libero, volutpat nec hendrerit at, faucibus in odio. Aliquam hendrerit nibh sed quam volutpat maximus. Nullam suscipit convallis lorem quis sodales. In tristique lobortis ante et dictum. Ut at finibus ipsum. In urna dolor, placerat et mi facilisis, congue sollicitudin massa. Phasellus felis turpis, cursus eu lectus et, porttitor malesuada augue. Sed feugiat volutpat velit, sollicitudin fringilla velit bibendum faucibus. """,
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
        return Align.center(Text("Option", justify="center"), vertical="middle")


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
            header=Widget(),
            content=Widget(
                Tweet(TweetBody(), Widget(classes={"button"})),
                Error(),
                Tweet(TweetBody()),
                Warning(),
                Tweet(TweetBody()),
                Success(),
            ),
            footer=Widget(),
            sidebar=Widget(
                Widget(classes={"title"}),
                Widget(classes={"user"}),
                OptionItem(),
                OptionItem(),
                OptionItem(),
                Widget(classes={"content"}),
            ),
        )

    async def on_key(self, event) -> None:
        await self.dispatch_key(event)

    def key_d(self):
        self.dark = not self.dark

    def key_x(self):
        self.panic(self.tree)


BasicApp.run(css_file="basic.css", watch_css=True, log="textual.log")
