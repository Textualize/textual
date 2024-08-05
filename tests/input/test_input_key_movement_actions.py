"""Unit tests for Input widget position movement actions."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Input


class InputTester(App[None]):
    """Input widget testing app."""

    def compose(self) -> ComposeResult:
        for value, input_id in (
            ("", "empty"),
            ("Shiny", "single-word"),
            ("Curse your sudden but inevitable betrayal", "multi-no-punctuation"),
            (
                "We have done the impossible, and that makes us mighty.",
                "multi-punctuation",
            ),
            ("Long as she does it quiet-like", "multi-and-hyphenated"),
        ):
            yield Input(value, id=input_id)


async def test_input_home() -> None:
    """Going home should always land at position zero."""
    async with InputTester().run_test() as pilot:
        for input in pilot.app.query(Input):
            input.action_home()
            assert input.cursor_position == 0


async def test_input_end() -> None:
    """Going end should always land at the last position."""
    async with InputTester().run_test() as pilot:
        for input in pilot.app.query(Input):
            input.action_end()
            assert input.cursor_position == len(input.value)


async def test_input_right_from_home() -> None:
    """Going right should always land at the next position, if there is one."""
    async with InputTester().run_test() as pilot:
        for input in pilot.app.query(Input):
            input.cursor_position = 0
            input.action_cursor_right()
            assert input.cursor_position == (1 if input.value else 0)


async def test_input_right_from_end() -> None:
    """Going right should always stay put if doing so from the end."""
    async with InputTester().run_test() as pilot:
        for input in pilot.app.query(Input):
            input.action_end()
            input.action_cursor_right()
            assert input.cursor_position == len(input.value)


async def test_input_left_from_home() -> None:
    """Going left from home should stay put."""
    async with InputTester().run_test() as pilot:
        for input in pilot.app.query(Input):
            input.cursor_position = 0
            input.action_cursor_left()
            assert input.cursor_position == 0


async def test_input_left_from_end() -> None:
    """Going left from the end should go back one place, where possible."""
    async with InputTester().run_test() as pilot:
        for input in pilot.app.query(Input):
            input.action_end()
            input.action_cursor_left()
            assert input.cursor_position == (len(input.value) - 1 if input.value else 0)


async def test_input_left_word_from_home() -> None:
    """Going left one word from the start should do nothing."""
    async with InputTester().run_test() as pilot:
        for input in pilot.app.query(Input):
            input.cursor_position = 0
            input.action_cursor_left_word()
            assert input.cursor_position == 0


async def test_input_left_word_from_end() -> None:
    """Going left one word from the end should land correctly.."""
    async with InputTester().run_test() as pilot:
        expected_at: dict[str | None, int] = {
            "empty": 0,
            "single-word": 0,
            "multi-no-punctuation": 33,
            "multi-punctuation": 47,
            "multi-and-hyphenated": 26,
        }
        for input in pilot.app.query(Input):
            input.action_end()
            input.action_cursor_left_word()
            assert input.cursor_position == expected_at[input.id]


async def test_password_input_left_word_from_end() -> None:
    """Going left one word from the end in a password field should land at home."""
    async with InputTester().run_test() as pilot:
        for input in pilot.app.query(Input):
            input.action_end()
            input.password = True
            input.action_cursor_left_word()
            assert input.cursor_position == 0


async def test_input_right_word_from_home() -> None:
    """Going right one word from the start should land correctly.."""
    async with InputTester().run_test() as pilot:
        expected_at: dict[str | None, int] = {
            "empty": 0,
            "single-word": 5,
            "multi-no-punctuation": 6,
            "multi-punctuation": 3,
            "multi-and-hyphenated": 5,
        }
        for input in pilot.app.query(Input):
            input.cursor_position = 0
            input.action_cursor_right_word()
            assert input.cursor_position == expected_at[input.id]


async def test_password_input_right_word_from_home() -> None:
    """Going right one word from the start of a password input should go to the end."""
    async with InputTester().run_test() as pilot:
        for input in pilot.app.query(Input):
            input.password = True
            input.action_cursor_right_word()
            assert input.cursor_position == len(input.value)


async def test_input_right_word_from_end() -> None:
    """Going right one word from the end should do nothing."""
    async with InputTester().run_test() as pilot:
        for input in pilot.app.query(Input):
            input.action_end()
            input.action_cursor_right_word()
            assert input.cursor_position == len(input.value)


async def test_input_right_word_to_the_end() -> None:
    """Using right-word to get to the end should hop the correct number of times."""
    async with InputTester().run_test() as pilot:
        expected_hops: dict[str | None, int] = {
            "empty": 0,
            "single-word": 1,
            "multi-no-punctuation": 6,
            "multi-punctuation": 10,
            "multi-and-hyphenated": 7,
        }
        for input in pilot.app.query(Input):
            input.cursor_position = 0
            hops = 0
            while input.cursor_position < len(input.value):
                input.action_cursor_right_word()
                hops += 1
            assert hops == expected_hops[input.id]


async def test_input_left_word_from_the_end() -> None:
    """Using left-word to get home from the end should hop the correct number of times."""
    async with InputTester().run_test() as pilot:
        expected_hops: dict[str | None, int] = {
            "empty": 0,
            "single-word": 1,
            "multi-no-punctuation": 6,
            "multi-punctuation": 10,
            "multi-and-hyphenated": 7,
        }
        for input in pilot.app.query(Input):
            input.action_end()
            hops = 0
            while input.cursor_position:
                input.action_cursor_left_word()
                hops += 1
            assert hops == expected_hops[input.id]


# TODO: more tests.
