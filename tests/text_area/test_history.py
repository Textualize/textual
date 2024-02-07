import pytest

from textual.app import App, ComposeResult
from textual.widgets import TextArea

SIMPLE_TEXT = """\
ABCDE
FGHIJ
KLMNO
PQRST
UVWXY
Z
"""


class TextAreaApp(App):
    def compose(self) -> ComposeResult:
        self.text_area = TextArea(SIMPLE_TEXT)
        yield self.text_area


@pytest.fixture
async def pilot():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        yield pilot


async def test_simple_undo(pilot):
    text_area: TextArea = pilot.app.text_area

    text_area.insert("123", (0, 0))

    assert text_area.text == "123" + SIMPLE_TEXT

    text_area.undo()

    assert text_area.text == SIMPLE_TEXT
