import string

import pytest

from textual.app import App, ComposeResult
from textual.suggester import SuggestFromList
from textual.widgets import Input


class SuggestionsApp(App[ComposeResult]):
    def __init__(self, suggestions):
        self.suggestions = suggestions
        self.input = Input(suggester=SuggestFromList(self.suggestions))
        super().__init__()

    def compose(self) -> ComposeResult:
        yield self.input


async def test_no_suggestions():
    app = SuggestionsApp([])
    async with app.run_test() as pilot:
        assert app.input._suggestion == ""
        await pilot.press("a")
        assert app.input._suggestion == ""


async def test_suggestion():
    app = SuggestionsApp(["hello"])
    async with app.run_test() as pilot:
        for char in "hello":
            await pilot.press(char)
            assert app.input._suggestion == "hello"


async def test_accept_suggestion():
    app = SuggestionsApp(["hello"])
    async with app.run_test() as pilot:
        await pilot.press("h")
        await pilot.press("right")
        assert app.input.value == "hello"


async def test_no_suggestion_on_empty_value():
    app = SuggestionsApp(["hello"])
    async with app.run_test():
        assert app.input._suggestion == ""


async def test_no_suggestion_on_empty_value_after_deleting():
    app = SuggestionsApp(["hello"])
    async with app.run_test() as pilot:
        await pilot.press("h", "e", "backspace", "backspace")
        assert app.input.value == ""  # Sanity check.
        assert app.input._suggestion == ""


async def test_suggestion_shows_up_after_deleting_extra_chars():
    app = SuggestionsApp(["hello"])
    async with app.run_test() as pilot:
        await pilot.press(*"help")
        assert app.input._suggestion == ""
        await pilot.press("backspace")
        assert app.input._suggestion == "hello"


async def test_suggestion_shows_up_after_deleting_extra_chars_in_middle_of_word():
    app = SuggestionsApp(["hello"])
    async with app.run_test() as pilot:
        await pilot.press(*"hefl")
        assert app.input._suggestion == ""
        await pilot.press("left", "backspace")
        assert app.input._suggestion == "hello"


@pytest.mark.parametrize(
    ("suggestion", "truncate_at"),
    [
        (".......", 3),
        ("hey there", 3),
        ("Olá, tudo bem?", 3),
        ("áàóãõñç", 2),
        (string.punctuation, 3),
        (string.punctuation[::-1], 5),
        (string.punctuation[::3], 5),
    ],
)
async def test_suggestion_with_special_characters(suggestion: str, truncate_at: int):
    app = SuggestionsApp([suggestion])
    async with app.run_test() as pilot:
        await pilot.press(*suggestion[:truncate_at])
        assert app.input._suggestion == suggestion


async def test_suggestion_priority():
    app = SuggestionsApp(["dog", "dad"])
    async with app.run_test() as pilot:
        await pilot.press("d")
        assert app.input._suggestion == "dog"
        await pilot.press("a")
        assert app.input._suggestion == "dad"
