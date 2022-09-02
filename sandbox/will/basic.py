from rich.console import RenderableType

from rich.syntax import Syntax
from rich.text import Text

from textual.app import App, ComposeResult
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import Static, DataTable, DirectoryTree, Header, Footer
from textual.layout import Container

CODE = '''
from __future__ import annotations

from typing import Iterable, TypeVar

T = TypeVar("T")


def loop_first(values: Iterable[T]) -> Iterable[tuple[bool, T]]:
    """Iterate and generate a tuple with a flag for first value."""
    iter_values = iter(values)
    try:
        value = next(iter_values)
    except StopIteration:
        return
    yield True, value
    for value in iter_values:
        yield False, value


def loop_last(values: Iterable[T]) -> Iterable[tuple[bool, T]]:
    """Iterate and generate a tuple with a flag for last value."""
    iter_values = iter(values)
    try:
        previous_value = next(iter_values)
    except StopIteration:
        return
    for value in iter_values:
        yield False, previous_value
        previous_value = value
    yield True, previous_value


def loop_first_last(values: Iterable[T]) -> Iterable[tuple[bool, bool, T]]:
    """Iterate and generate a tuple with a flag for first and last value."""
    iter_values = iter(values)
    try:
        previous_value = next(iter_values)
    except StopIteration:
        return
    first = True
    for value in iter_values:
        yield first, False, previous_value
        first = False
        previous_value = value
    yield first, True, previous_value
'''


lorem_short = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. In velit liber a a a, volutpat nec hendrerit at, faucibus in odio. Aliquam hendrerit nibh sed quam volutpat maximus. Nullam suscipit convallis lorem quis sodales. In tristique lobortis ante et dictum. Ut at finibus ipsum."""
lorem = (
    lorem_short
    + """ In urna dolor, placerat et mi facilisis, congue sollicitudin massa. Phasellus felis turpis, cursus eu lectus et, porttitor malesuada augue. Sed feugiat volutpat velit, sollicitudin fringilla velit bibendum faucibus. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In velit libero, volutpat nec hendrerit at, faucibus in odio. Aliquam hendrerit nibh sed quam volutpat maximus. Nullam suscipit convallis lorem quis sodales. In tristique lobortis ante et dictum. Ut at finibus ipsum. In urna dolor, placerat et mi facilisis, congue sollicitudin massa. Phasellus felis turpis, cursus eu lectus et, porttitor malesuada augue. Sed feugiat volutpat velit, sollicitudin fringilla velit bibendum faucibus. """
)

lorem_short_text = Text.from_markup(lorem_short)
lorem_long_text = Text.from_markup(lorem * 2)


class TweetHeader(Widget):
    def render(self) -> RenderableType:
        return Text("Lorem Impsum", justify="center")


class TweetBody(Widget):
    short_lorem = Reactive(False)

    def render(self) -> Text:
        return lorem_short_text if self.short_lorem else lorem_long_text


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
        return Text("This is a success  message", justify="center")


class BasicApp(App, css_path="basic.css"):
    """A basic app demonstrating CSS"""

    def on_load(self):
        """Bind keys here."""
        self.bind("s", "toggle_class('#sidebar', '-active')", description="Sidebar")
        self.bind("d", "toggle_dark", description="Dark mode")
        self.bind("q", "quit", description="Quit")
        self.bind("f", "query_test", description="Query test")

    def compose(self):
        yield Header()

        table = DataTable()
        self.scroll_to_target = Tweet(TweetBody())

        yield Container(
            Tweet(TweetBody()),
            Widget(
                Static(
                    Syntax(CODE, "python", line_numbers=True, indent_guides=True),
                    classes="code",
                ),
                classes="scrollable",
            ),
            table,
            Widget(DirectoryTree("~/"), id="tree-container"),
            Error(),
            Tweet(TweetBody(), classes="scrollbar-size-custom"),
            Warning(),
            Tweet(TweetBody(), classes="scroll-horizontal"),
            Success(),
            Tweet(TweetBody(), classes="scroll-horizontal"),
            Tweet(TweetBody(), classes="scroll-horizontal"),
            Tweet(TweetBody(), classes="scroll-horizontal"),
            Tweet(TweetBody(), classes="scroll-horizontal"),
            Tweet(TweetBody(), classes="scroll-horizontal"),
        )
        yield Widget(
            Widget(classes="title"),
            Widget(classes="user"),
            OptionItem(),
            OptionItem(),
            OptionItem(),
            Widget(classes="content"),
            id="sidebar",
        )
        yield Footer()

        table.add_column("Foo", width=20)
        table.add_column("Bar", width=20)
        table.add_column("Baz", width=20)
        table.add_column("Foo", width=20)
        table.add_column("Bar", width=20)
        table.add_column("Baz", width=20)
        table.zebra_stripes = True
        for n in range(100):
            table.add_row(*[f"Cell ([b]{n}[/b], {col})" for col in range(6)])

    def on_mount(self):
        self.sub_title = "Widget demo"

    async def on_key(self, event) -> None:
        await self.dispatch_key(event)

    def action_toggle_dark(self):
        self.dark = not self.dark

    def action_query_test(self):
        query = self.query("Tweet")
        self.log(query)
        self.log(query.nodes)
        self.log(query)
        self.log(query.nodes)

        query.set_styles("outline: outer red;")

        query = query.exclude(".scroll-horizontal")
        self.log(query)
        self.log(query.nodes)

        # query = query.filter(".rubbish")
        # self.log(query)
        # self.log(query.first())

    async def key_q(self):
        await self.shutdown()

    def key_x(self):
        self.panic(self.tree)

    def key_escape(self):
        self.app.bell()

    def key_t(self):
        # Pressing "t" toggles the content of the TweetBody widget, from a long "Lorem ipsum..." to a shorter one.
        tweet_body = self.query("TweetBody").first()
        tweet_body.short_lorem = not tweet_body.short_lorem

    def key_v(self):
        self.get_child(id="content").scroll_to_widget(self.scroll_to_target)

    def key_space(self):
        self.bell()


app = BasicApp()

if __name__ == "__main__":
    app.run()

    # from textual.geometry import Region
    # from textual.color import Color

    # print(Region.intersection.cache_info())
    # print(Region.overlaps.cache_info())
    # print(Region.union.cache_info())
    # print(Region.split_vertical.cache_info())
    # print(Region.__contains__.cache_info())
    # from textual.css.scalar import Scalar

    # print(Scalar.resolve_dimension.cache_info())

    # from rich.style import Style
    # from rich.cells import cached_cell_len

    # print(Style._add.cache_info())

    # print(cached_cell_len.cache_info())
