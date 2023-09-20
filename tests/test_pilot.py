from string import punctuation

import pytest

from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.pilot import OutOfBounds
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


@pytest.mark.parametrize(
    ["screen_size", "offset"],
    [
        # Screen size is 80 x 24.
        ((80, 24), (100, 12)),  # Right of screen.
        ((80, 24), (100, 36)),  # Bottom-right of screen.
        ((80, 24), (50, 36)),  # Under screen.
        ((80, 24), (-10, 36)),  # Bottom-left of screen.
        ((80, 24), (-10, 12)),  # Left of screen.
        ((80, 24), (-10, -2)),  # Top-left of screen.
        ((80, 24), (50, -2)),  # Above screen.
        ((80, 24), (100, -2)),  # Top-right of screen.
        # Screen size is 5 x 5.
        ((5, 5), (7, 3)),  # Right of screen.
        ((5, 5), (7, 7)),  # Bottom-right of screen.
        ((5, 5), (3, 7)),  # Under screen.
        ((5, 5), (-1, 7)),  # Bottom-left of screen.
        ((5, 5), (-1, 3)),  # Left of screen.
        ((5, 5), (-1, -1)),  # Top-left of screen.
        ((5, 5), (3, -1)),  # Above screen.
        ((5, 5), (7, -1)),  # Top-right of screen.
    ],
)
async def test_pilot_click_outside_screen_errors(screen_size, offset):
    app = App()
    async with app.run_test(size=screen_size) as pilot:
        with pytest.raises(OutOfBounds):
            await pilot.click(offset=offset)


@pytest.mark.parametrize(
    ["screen_size", "offset"],
    [
        # Screen size is 80 x 24.
        ((80, 24), (100, 12)),  # Right of screen.
        ((80, 24), (100, 36)),  # Bottom-right of screen.
        ((80, 24), (50, 36)),  # Under screen.
        ((80, 24), (-10, 36)),  # Bottom-left of screen.
        ((80, 24), (-10, 12)),  # Left of screen.
        ((80, 24), (-10, -2)),  # Top-left of screen.
        ((80, 24), (50, -2)),  # Above screen.
        ((80, 24), (100, -2)),  # Top-right of screen.
        # Screen size is 5 x 5.
        ((5, 5), (7, 3)),  # Right of screen.
        ((5, 5), (7, 7)),  # Bottom-right of screen.
        ((5, 5), (3, 7)),  # Under screen.
        ((5, 5), (-1, 7)),  # Bottom-left of screen.
        ((5, 5), (-1, 3)),  # Left of screen.
        ((5, 5), (-1, -1)),  # Top-left of screen.
        ((5, 5), (3, -1)),  # Above screen.
        ((5, 5), (7, -1)),  # Top-right of screen.
    ],
)
async def test_pilot_hover_outside_screen_errors(screen_size, offset):
    app = App()
    async with app.run_test(size=screen_size) as pilot:
        with pytest.raises(OutOfBounds):
            await pilot.hover(offset=offset)
