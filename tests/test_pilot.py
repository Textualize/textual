from string import punctuation

import pytest

from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Label

KEY_CHARACTERS_TO_TEST = "akTW03" + punctuation
"""Test some "simple" characters (letters + digits) and all punctuation."""


async def test_pilot_press_ascii_chars():
    """Test that the pilot can press most ASCII characters as keys."""
    keys_pressed = []

    class TestApp(App[None]):
        def on_key(self, event: events.Key) -> None:
            keys_pressed.append(event.character)

    async with TestApp().run_test() as pilot:
        for char in KEY_CHARACTERS_TO_TEST:
            await pilot.press(char)
            assert keys_pressed[-1] == char


async def test_pilot_exception_catching_compose():
    """Ensuring that test frameworks are aware of exceptions
    inside compose methods when running via Pilot run_test()."""

    class FailingApp(App):
        def compose(self) -> ComposeResult:
            1 / 0
            yield Label("Beep")

    with pytest.raises(ZeroDivisionError):
        async with FailingApp().run_test():
            pass


async def test_pilot_exception_catching_action():
    """Ensure that exceptions inside action handlers are presented
    to the test framework when running via Pilot run_test()."""

    class FailingApp(App):
        BINDINGS = [Binding("b", "beep", "beep")]

        def action_beep(self) -> None:
            1 / 0

    with pytest.raises(ZeroDivisionError):
        async with FailingApp().run_test() as pilot:
            await pilot.press("b")
