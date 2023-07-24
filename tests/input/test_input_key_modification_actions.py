"""Unit tests for Input widget value modification actions."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Input

TEST_INPUTS: dict[str | None, str] = {
    "empty": "",
    "multi-no-punctuation": "Curse your sudden but inevitable betrayal",
    "multi-punctuation": "We have done the impossible, and that makes us mighty.",
    "multi-and-hyphenated": "Long as she does it quiet-like",
}


class InputTester(App[None]):
    """Input widget testing app."""

    def compose(self) -> ComposeResult:
        for input_id, value in TEST_INPUTS.items():
            yield Input(value, id=input_id)


async def test_delete_left_from_home() -> None:
    """Deleting left from home should do nothing."""
    async with InputTester().run_test() as pilot:
        for input in pilot.app.query(Input):
            input.action_delete_left()
            assert input.cursor_position == 0
            assert input.value == TEST_INPUTS[input.id]


async def test_delete_left_from_end() -> None:
    """Deleting left from end should remove the last character (if there is one)."""
    async with InputTester().run_test() as pilot:
        for input in pilot.app.query(Input):
            input.action_end()
            input.action_delete_left()
            assert input.cursor_position == len(input.value)
            assert input.value == TEST_INPUTS[input.id][:-1]


async def test_delete_left_word_from_home() -> None:
    """Deleting word left from home should do nothing."""
    async with InputTester().run_test() as pilot:
        for input in pilot.app.query(Input):
            input.action_delete_left_word()
            assert input.cursor_position == 0
            assert input.value == TEST_INPUTS[input.id]


async def test_delete_left_word_from_inside_first_word() -> None:
    async with InputTester().run_test() as pilot:
        for input in pilot.app.query(Input):
            input.cursor_position = 1
            input.action_delete_left_word()
            assert input.cursor_position == 0
            assert input.value == TEST_INPUTS[input.id][1:]


async def test_delete_left_word_from_end() -> None:
    """Deleting word left from end should remove the expected text."""
    async with InputTester().run_test() as pilot:
        expected: dict[str | None, str] = {
            "empty": "",
            "multi-no-punctuation": "Curse your sudden but inevitable ",
            "multi-punctuation": "We have done the impossible, and that makes us ",
            "multi-and-hyphenated": "Long as she does it quiet-",
        }
        for input in pilot.app.query(Input):
            input.action_end()
            input.action_delete_left_word()
            assert input.cursor_position == len(input.value)
            assert input.value == expected[input.id]


async def test_password_delete_left_word_from_end() -> None:
    """Deleting word left from end of a password input should delete everything."""
    async with InputTester().run_test() as pilot:
        for input in pilot.app.query(Input):
            input.action_end()
            input.password = True
            input.action_delete_left_word()
            assert input.cursor_position == 0
            assert input.value == ""


async def test_delete_left_all_from_home() -> None:
    """Deleting all left from home should do nothing."""
    async with InputTester().run_test() as pilot:
        for input in pilot.app.query(Input):
            input.action_delete_left_all()
            assert input.cursor_position == 0
            assert input.value == TEST_INPUTS[input.id]


async def test_delete_left_all_from_end() -> None:
    """Deleting all left from end should empty the input value."""
    async with InputTester().run_test() as pilot:
        for input in pilot.app.query(Input):
            input.action_end()
            input.action_delete_left_all()
            assert input.cursor_position == 0
            assert input.value == ""


async def test_delete_right_from_home() -> None:
    """Deleting right from home should delete one character (if there is any to delete)."""
    async with InputTester().run_test() as pilot:
        for input in pilot.app.query(Input):
            input.action_delete_right()
            assert input.cursor_position == 0
            assert input.value == TEST_INPUTS[input.id][1:]


async def test_delete_right_from_end() -> None:
    """Deleting right from end should not change the input's value."""
    async with InputTester().run_test() as pilot:
        for input in pilot.app.query(Input):
            input.action_end()
            input.action_delete_right()
            assert input.cursor_position == len(input.value)
            assert input.value == TEST_INPUTS[input.id]


async def test_delete_right_word_from_home() -> None:
    """Deleting word right from home should delete one word (if there is one)."""
    async with InputTester().run_test() as pilot:
        expected: dict[str | None, str] = {
            "empty": "",
            "multi-no-punctuation": "your sudden but inevitable betrayal",
            "multi-punctuation": "have done the impossible, and that makes us mighty.",
            "multi-and-hyphenated": "as she does it quiet-like",
        }
        for input in pilot.app.query(Input):
            input.action_delete_right_word()
            assert input.cursor_position == 0
            assert input.value == expected[input.id]


async def test_password_delete_right_word_from_home() -> None:
    """Deleting word right from home of a password input should delete everything."""
    async with InputTester().run_test() as pilot:
        for input in pilot.app.query(Input):
            input.password = True
            input.action_delete_right_word()
            assert input.cursor_position == 0
            assert input.value == ""


async def test_delete_right_word_from_end() -> None:
    """Deleting word right from end should not change the input's value."""
    async with InputTester().run_test() as pilot:
        for input in pilot.app.query(Input):
            input.action_end()
            input.action_delete_right_word()
            assert input.cursor_position == len(input.value)
            assert input.value == TEST_INPUTS[input.id]


async def test_delete_right_all_from_home() -> None:
    """Deleting all right home should remove everything in the input."""
    async with InputTester().run_test() as pilot:
        for input in pilot.app.query(Input):
            input.action_delete_right_all()
            assert input.cursor_position == 0
            assert input.value == ""


async def test_delete_right_all_from_end() -> None:
    """Deleting all right from end should not change the input's value."""
    async with InputTester().run_test() as pilot:
        for input in pilot.app.query(Input):
            input.action_end()
            input.action_delete_right_all()
            assert input.cursor_position == len(input.value)
            assert input.value == TEST_INPUTS[input.id]
