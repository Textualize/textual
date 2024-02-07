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


async def test_simple_undo_redo(pilot):
    text_area: TextArea = pilot.app.text_area

    text_area.insert("123", (0, 0))

    assert text_area.text == "123" + SIMPLE_TEXT
    text_area.undo()
    assert text_area.text == SIMPLE_TEXT
    text_area.redo()
    assert text_area.text == "123" + SIMPLE_TEXT


async def test_undo_selection_retained(pilot):
    text_area: TextArea = pilot.app.text_area
    text_area.delete((0, 0), (2, 3))
    assert text_area.text == "NO\nPQRST\nUVWXY\nZ\n"
    text_area.undo()
    # assert text_area.selection ==
