from string import punctuation

from textual import events
from textual.app import App

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
