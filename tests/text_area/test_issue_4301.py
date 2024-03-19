from itertools import product

import pytest

from textual.app import App, ComposeResult
from textual.widgets import TextArea
from textual.widgets.text_area import Selection

TEST_TEXT = "\n".join(f"01234567890 - {n}" for n in range(10))
TEST_SELECTED_TEXT = "567890 - 0\n01234567890 - 1\n01234"


class TextAreaApp(App[None]):

    def compose(self) -> ComposeResult:
        yield TextArea(TEST_TEXT)


@pytest.mark.parametrize(
    "selection, edit",
    product(
        [Selection((0, 5), (2, 5)), Selection((2, 5), (0, 5))],
        ["A", "delete", "backspace"],
    ),
)
async def test_issue_4301_reproduction(selection: Selection, edit: str) -> None:
    """Test https://github.com/Textualize/textual/issues/4301"""

    async with (app := TextAreaApp()).run_test() as pilot:
        assert app.query_one(TextArea).text == TEST_TEXT
        app.query_one(TextArea).selection = selection
        assert app.query_one(TextArea).selected_text == TEST_SELECTED_TEXT
        await pilot.press(edit)
        await pilot.press("ctrl+z")
        assert app.query_one(TextArea).text == TEST_TEXT
        # Note that the real test here is that the following code doesn't
        # result in a crash; everything above should really be a given.
        await pilot.press(*(["down"] * 10))
