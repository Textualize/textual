from contextlib import asynccontextmanager
import pytest

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget


@asynccontextmanager
async def run_app():
    class HorizontalAutoWidth(App):
        def compose(self) -> ComposeResult:
            child1 = Widget(id="child1")
            child1.styles.width = 4
            child2 = Widget(id="child2")
            child2.styles.width = 6
            child3 = Widget(id="child3")
            child3.styles.width = 5
            self.horizontal = Horizontal(child1, child2, child3)
            yield self.horizontal

    app = HorizontalAutoWidth()
    async with app.run_test():
        yield app


async def test_horizontal_get_content_width():
    async with run_app() as app:
        size = app.screen.size
        width = app.horizontal.get_content_width(size, size)
        assert width == 15
