"""Test basic functioning of some containers."""

from textual.app import App, ComposeResult
from textual.containers import (
    Center,
    Horizontal,
    HorizontalScroll,
    Middle,
    Vertical,
    VerticalScroll,
)
from textual.widgets import Label


async def test_horizontal_vs_horizontalscroll_scrolling():
    """Check the default scrollbar behaviours for `Horizontal` and `HorizontalScroll`."""

    class HorizontalsApp(App[None]):
        CSS = """
        Screen {
            layout: vertical;
        }
        """

        def compose(self) -> ComposeResult:
            with Horizontal():
                for _ in range(10):
                    yield Label("How is life going? " * 3 + " | ")
            with HorizontalScroll():
                for _ in range(10):
                    yield Label("How is life going? " * 3 + " | ")

    WIDTH = 80
    HEIGHT = 24
    app = HorizontalsApp()
    async with app.run_test(size=(WIDTH, HEIGHT)):
        horizontal = app.query_one(Horizontal)
        horizontal_scroll = app.query_one(HorizontalScroll)
        assert horizontal.size.height == horizontal_scroll.size.height
        assert horizontal.scrollbars_enabled == (False, False)
        assert horizontal_scroll.scrollbars_enabled == (False, True)


async def test_vertical_vs_verticalscroll_scrolling():
    """Check the default scrollbar behaviours for `Vertical` and `VerticalScroll`."""

    class VerticalsApp(App[None]):
        CSS = """
        Screen {
            layout: horizontal;
        }
        """

        def compose(self) -> ComposeResult:
            with Vertical():
                for _ in range(10):
                    yield Label("How is life going?\n" * 3 + "\n\n")
            with VerticalScroll():
                for _ in range(10):
                    yield Label("How is life going?\n" * 3 + "\n\n")

    WIDTH = 80
    HEIGHT = 24
    app = VerticalsApp()
    async with app.run_test(size=(WIDTH, HEIGHT)):
        vertical = app.query_one(Vertical)
        vertical_scroll = app.query_one(VerticalScroll)
        assert vertical.size.width == vertical_scroll.size.width
        assert vertical.scrollbars_enabled == (False, False)
        assert vertical_scroll.scrollbars_enabled == (True, False)


async def test_center_container():
    """Check the size of the container `Center`."""

    class CenterApp(App[None]):
        def compose(self) -> ComposeResult:
            with Center():
                yield Label("<>\n<>\n<>")

    app = CenterApp()
    async with app.run_test():
        center = app.query_one(Center)
        assert center.size.width == app.size.width
        assert center.size.height == 3


async def test_middle_container():
    """Check the size of the container `Middle`."""

    class MiddleApp(App[None]):
        def compose(self) -> ComposeResult:
            with Middle():
                yield Label("1234")

    app = MiddleApp()
    async with app.run_test():
        middle = app.query_one(Middle)
        assert middle.size.width == 4
        assert middle.size.height == app.size.height


async def test_scrollbar_zero_thickness():
    """Ensuring that scrollbars can be set to zero thickness."""

    class ScrollbarZero(App):
        CSS = """* {
            scrollbar-size: 0 0;
            scrollbar-size-vertical: 0;  /* just exercising the parser */
            scrollbar-size-horizontal: 0;  /* exercise the parser */
        }
        """

        def compose(self) -> ComposeResult:
            with Vertical():
                for _ in range(10):
                    yield Label("Hello, world!")

    app = ScrollbarZero()
    async with app.run_test(size=(8, 6)):
        pass
