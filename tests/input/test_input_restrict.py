import re

import pytest

from textual.app import App, ComposeResult
from textual.widgets import Input
from textual.widgets._input import _RESTRICT_TYPES


def test_input_number_type():
    """Test number type regex."""
    number = _RESTRICT_TYPES["number"]
    assert re.fullmatch(number, "0")
    assert re.fullmatch(number, "0.")
    assert re.fullmatch(number, ".")
    assert re.fullmatch(number, ".0")
    assert re.fullmatch(number, "1.1")
    assert re.fullmatch(number, "1e1")
    assert re.fullmatch(number, "1.2e")
    assert re.fullmatch(number, "1.2e10")
    assert re.fullmatch(number, "1.2E10")
    assert re.fullmatch(number, "1.2e-")
    assert re.fullmatch(number, "1.2e-10")
    assert not re.fullmatch(number, "1.2e10e")
    assert not re.fullmatch(number, "1f2")
    assert not re.fullmatch(number, "inf")
    assert not re.fullmatch(number, "nan")


def test_input_integer_type():
    """Test input type regex"""
    integer = _RESTRICT_TYPES["integer"]
    assert re.fullmatch(integer, "0")
    assert re.fullmatch(integer, "1")
    assert re.fullmatch(integer, "10")
    assert re.fullmatch(integer, "123456789")
    assert re.fullmatch(integer, "-")
    assert re.fullmatch(integer, "+")
    assert re.fullmatch(integer, "-1")
    assert re.fullmatch(integer, "+2")
    assert not re.fullmatch(integer, "+2e")
    assert not re.fullmatch(integer, "foo")


async def test_bad_type():
    """Check an invalid type raises a ValueError."""

    class InputApp(App):
        def compose(self) -> ComposeResult:
            yield Input(type="foo")  # Bad type

    app = InputApp()

    with pytest.raises(ValueError):
        async with app.run_test():
            pass


async def test_max_length():
    """Check max_length limits characters."""

    class InputApp(App):
        AUTO_FOCUS = "Input"

        def compose(self) -> ComposeResult:
            yield Input(max_length=5)

    async with InputApp().run_test() as pilot:
        input_widget = pilot.app.query_one(Input)
        await pilot.press("1")
        assert input_widget.value == "1"
        await pilot.press("2", "3", "4", "5")
        assert input_widget.value == "12345"
        # Value is max length, no more characters are permitted
        await pilot.press("6")
        assert input_widget.value == "12345"
        await pilot.press("7")
        assert input_widget.value == "12345"
        # Backspace is ok
        await pilot.press("backspace")
        assert input_widget.value == "1234"
        await pilot.press("0")
        assert input_widget.value == "12340"
        # Back to maximum
        await pilot.press("1")
        assert input_widget.value == "12340"


async def test_restrict():
    """Test restriction by regex."""

    class InputApp(App):
        AUTO_FOCUS = "Input"

        def compose(self) -> ComposeResult:
            yield Input(restrict="[abc]*")

    async with InputApp().run_test() as pilot:
        input_widget = pilot.app.query_one(Input)
        await pilot.press("a")
        assert input_widget.value == "a"
        await pilot.press("b")
        assert input_widget.value == "ab"
        await pilot.press("c")
        assert input_widget.value == "abc"
        # "d" is restricted
        await pilot.press("d")
        assert input_widget.value == "abc"
        # "a" is not
        await pilot.press("a")
        assert input_widget.value == "abca"


async def test_restrict_type():
    class InputApp(App):
        def compose(self) -> ComposeResult:
            yield Input(type="integer", id="integer")
            yield Input(type="number", id="number")
            yield Input(type="text", id="text")

    async with InputApp().run_test() as pilot:
        integer_input = pilot.app.query_one("#integer", Input)
        number_input = pilot.app.query_one("#number", Input)
        text_input = pilot.app.query_one("#text", Input)

        integer_input.focus()
        await pilot.press("a")
        assert integer_input.value == ""

        await pilot.press("-")
        assert integer_input.is_valid is False

        await pilot.press("1")
        assert integer_input.value == "-1"
        assert integer_input.is_valid is True

        number_input.focus()
        await pilot.press("x")
        assert number_input.value == ""
        await pilot.press("-", "3", ".", "1", "4", "y")
        assert number_input.value == "-3.14"

        text_input.focus()
        await pilot.press("!", "x", "9")
        assert text_input.value == "!x9"
