import pytest

from textual.geometry import Offset
from textual.selection import Selection


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
