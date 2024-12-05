from __future__ import annotations

import pytest

from textual.app import App, ComposeResult
from textual.widgets import Input

_FORWARD_DELETIONS = [
    ((0, 0), "0123456789"),  # Delete nothing
    ((0, 10), ""),  # Delete all
    ((0, 1), "123456789"),  # Delete first character
    ((5, 10), "01234"),  # Delete last 5 characters
    ((3, 6), "0126789"),  # Delete middle 3 characters
    ((5, 20), "01234"),  # Delete past end results in clamp
]
_REVERSE_DELETIONS = [
    ((end, start), value_after) for (start, end), value_after in _FORWARD_DELETIONS
]
DELETIONS = _FORWARD_DELETIONS + _REVERSE_DELETIONS
"""The same deletions performed in both forward and reverse directions."""


@pytest.mark.parametrize("selection,value_after", DELETIONS)
async def test_input_delete(selection: tuple[int, int], value_after: str):
    class InputApp(App[None]):
        TEST_TEXT = "0123456789"

        def compose(self) -> ComposeResult:
            yield Input(self.TEST_TEXT)

    async with InputApp().run_test() as pilot:
        app = pilot.app
        input = app.query_one(Input)
        input.delete(*selection)
        assert input.value == value_after


_FORWARD_REPLACEMENTS = [
    ((0, 0), "", "0123456789"),
    ((0, 1), "X", "X123456789"),  # Replace first character with "X"
    ((5, 10), "X", "01234X"),  # Replace last 5 characters with "X"
    ((3, 6), "X", "012X6789"),  # Replace middle 3 characters with "X"
    ((5, 20), "X", "01234X"),  # Replace past end results in clamp
]
_REVERSE_REPLACEMENTS = [
    ((end, start), replacement, result)
    for (start, end), replacement, result in _FORWARD_REPLACEMENTS
]
REPLACEMENTS = _FORWARD_REPLACEMENTS + _REVERSE_REPLACEMENTS


@pytest.mark.parametrize("selection,replacement,result", REPLACEMENTS)
async def test_input_replace(selection: tuple[int, int], replacement: str, result: str):
    class InputApp(App[None]):
        TEST_TEXT = "0123456789"

        def compose(self) -> ComposeResult:
            yield Input(self.TEST_TEXT)

    async with InputApp().run_test() as pilot:
        app = pilot.app
        input = app.query_one(Input)
        input.replace(replacement, *selection)
        assert input.value == result
