from textual.app import App, ComposeResult
from textual.widgets import TextArea
from textual.widgets.text_area import Selection

TEST_TEXT = "\n".join(f"01234567890 - {n}" for n in range(10))
TEST_SELECTION = Selection((2, 5), (0, 5))
TEST_SELECTED_TEXT = "567890 - 0\n01234567890 - 1\n01234"
TEST_REPLACEMENT = "A"
TEST_RESULT_TEXT = TEST_TEXT.replace(TEST_SELECTED_TEXT, TEST_REPLACEMENT)


class TextAreaApp(App[None]):

    def compose(self) -> ComposeResult:
        yield TextArea(TEST_TEXT)


async def test_issue_4301_reproduction() -> None:

    async with (app := TextAreaApp()).run_test() as pilot:
        assert app.query_one(TextArea).text == TEST_TEXT
        app.query_one(TextArea).selection = TEST_SELECTION
        assert app.query_one(TextArea).selected_text == TEST_SELECTED_TEXT
        await pilot.press("A")
        assert app.query_one(TextArea).text == TEST_RESULT_TEXT
        await pilot.press("ctrl+z")
        assert app.query_one(TextArea).text == TEST_TEXT
        await pilot.press(*(["down"] * 10))
