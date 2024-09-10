import pytest

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget


@pytest.fixture
async def app():
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
    yield app


async def test_horizontal_get_content_width(app):
    async with app.run_test():
        size = app.screen.size
        width = app.horizontal.get_content_width(size, size)
        assert width == 15
