import pytest

from textual.app import App, ComposeResult
from textual.geometry import Offset
from textual.selection import Selection
from textual.widgets import Static


@pytest.mark.parametrize(
    "text,selection,expected",
    [
        ("Hello", Selection(None, None), "Hello"),
        ("Hello\nWorld", Selection(None, None), "Hello\nWorld"),
        ("Hello\nWorld", Selection(Offset(0, 1), None), "World"),
        ("Hello\nWorld", Selection(None, Offset(5, 0)), "Hello"),
        ("Foo", Selection(Offset(0, 0), Offset(1, 0)), "F"),
        ("Foo", Selection(Offset(1, 0), Offset(2, 0)), "o"),
        ("Foo", Selection(Offset(0, 0), Offset(2, 0)), "Fo"),
        ("Foo", Selection(Offset(0, 0), None), "Foo"),
    ],
)
def test_extract(text: str, selection: Selection, expected: str) -> None:
    """Test Selection.extract"""
    assert selection.extract(text) == expected


async def test_double_width():
    """Test that selection works with double width characters."""

    TEXT = """😂❤️👍Select😊🙏😍\nme🔥💯😭😂❤️👍"""

    class TextSelectApp(App):
        def compose(self) -> ComposeResult:
            yield Static(TEXT)

    app = TextSelectApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        assert await pilot.mouse_down(offset=(2, 0))
        await pilot.pause()
        assert await pilot.mouse_up(offset=(7, 1))
        selected_text = app.screen.get_selected_text()
        expected = "❤️👍Select😊🙏😍\nme🔥💯😭"

    assert selected_text == expected
