"""Tests for Input.max_length enforcement on programmatic value assignment."""
from __future__ import annotations

import pytest

from textual.app import App, ComposeResult
from textual.widgets import Input


class InputApp(App[None]):
    CSS = "Input { height: auto; }"

    def __init__(self, max_length: int = 0, initial: str = "") -> None:
        super().__init__()
        self._max_length = max_length
        self._initial = initial

    def compose(self) -> ComposeResult:
        yield Input(
            self._initial if self._initial else None,
            max_length=self._max_length,
        )


async def test_programmatic_value_truncated_when_exceeds_max_length():
    """Assigning a value longer than max_length truncates to max_length characters."""
    async with InputApp(max_length=5).run_test() as pilot:
        widget = pilot.app.query_one(Input)
        widget.value = "hello world"
        assert widget.value == "hello"


async def test_programmatic_value_preserved_when_within_max_length():
    """Assigning a value within max_length stores it unchanged."""
    async with InputApp(max_length=10).run_test() as pilot:
        widget = pilot.app.query_one(Input)
        widget.value = "hello"
        assert widget.value == "hello"


async def test_programmatic_value_preserved_when_equal_to_max_length():
    """Assigning a value exactly equal to max_length stores it unchanged."""
    async with InputApp(max_length=5).run_test() as pilot:
        widget = pilot.app.query_one(Input)
        widget.value = "hello"
        assert widget.value == "hello"


async def test_initial_value_truncated_when_exceeds_max_length():
    """An initial value longer than max_length is truncated at construction."""
    async with InputApp(max_length=3, initial="toolong").run_test() as pilot:
        widget = pilot.app.query_one(Input)
        assert widget.value == "too"


async def test_no_max_length_preserves_any_value():
    """When max_length is 0 (no limit), long strings are stored intact."""
    async with InputApp(max_length=0).run_test() as pilot:
        widget = pilot.app.query_one(Input)
        long_value = "a" * 1000
        widget.value = long_value
        assert widget.value == long_value


async def test_keyboard_input_still_enforces_max_length():
    """Typing characters beyond max_length is still rejected via keyboard."""
    async with InputApp(max_length=3).run_test() as pilot:
        await pilot.click(Input)
        await pilot.press("a", "b", "c", "d", "e")
        widget = pilot.app.query_one(Input)
        assert len(widget.value) <= 3
