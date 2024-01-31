import pytest

from textual.app import App
from textual.keys import _character_to_key, _get_key_display


@pytest.mark.parametrize(
    "character,key",
    [
        ("1", "1"),
        ("2", "2"),
        ("a", "a"),
        ("z", "z"),
        ("_", "underscore"),
        (" ", "space"),
        ("~", "tilde"),
        ("?", "question_mark"),
        ("£", "pound_sign"),
        (",", "comma"),
    ],
)
def test_character_to_key(character: str, key: str) -> None:
    assert _character_to_key(character) == key


async def test_character_bindings():
    """Test you can bind to a character as well as a longer key name."""
    counter = 0

    class BindApp(App):
        BINDINGS = [(".,~,space", "increment", "foo")]

        def action_increment(self) -> None:
            nonlocal counter
            counter += 1

    app = BindApp()
    async with app.run_test() as pilot:
        await pilot.press(".")
        await pilot.pause()
        assert counter == 1
        await pilot.press("~")
        await pilot.pause()
        assert counter == 2
        await pilot.press(" ")
        await pilot.pause()
        assert counter == 3
        await pilot.press("x")
        await pilot.pause()
        assert counter == 3


def test_get_key_display():
    assert _get_key_display("minus") == "-"


def test_get_key_display_when_used_in_conjunction():
    """Test a key display is the same if used in conjunction with another key.
    For example, "ctrl+right_square_bracket" should display the bracket as "]",
    the same as it would without the ctrl modifier.

    Regression test for #3035 https://github.com/Textualize/textual/issues/3035
    """

    right_square_bracket = _get_key_display("right_square_bracket")
    ctrl_right_square_bracket = _get_key_display("ctrl+right_square_bracket")
    assert ctrl_right_square_bracket == f"CTRL+{right_square_bracket}"

    left = _get_key_display("left")
    ctrl_left = _get_key_display("ctrl+left")
    assert ctrl_left == f"CTRL+{left}"
