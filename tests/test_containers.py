"""Test basic functioning of some containers."""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, HorizontalScroll
from textual.widgets import Label


async def test_horizontal_vs_horizontalscroll_scrolling():
    """Check the default scrollbar behaviours for Horizontal and HorizontalScroll."""

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
