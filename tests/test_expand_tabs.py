import pytest

from textual.expand_tabs import expand_tabs_inline, get_tab_widths


@pytest.mark.parametrize(
    "line, expanded_line",
    [
        (" b ar ", " b ar "),
        ("\tbar", "    bar"),
        ("\tbar\t", "    bar "),
        ("\tr\t", "    r   "),
        ("1\tbar", "1   bar"),
        ("12\tbar", "12  bar"),
        ("123\tbar", "123 bar"),
        ("1234\tbar", "1234    bar"),
        ("💩\tbar", "💩  bar"),
        ("💩💩\tbar", "💩💩    bar"),
        ("💩💩💩\tbar", "💩💩💩  bar"),
        ("F💩\tbar", "F💩 bar"),
        ("F💩O\tbar", "F💩O    bar"),
    ],
)
def test_expand_tabs_inline(line, expanded_line):
    assert expand_tabs_inline(line) == expanded_line


def test_get_tab_widths():
    assert get_tab_widths("\tbar") == [("", 4), ("bar", 0)]
    assert get_tab_widths("\tbar\t") == [("", 4), ("bar", 1)]
    assert get_tab_widths("\tfoo\t\t") == [("", 4), ("foo", 1), ("", 4)]
    assert get_tab_widths("\t木foo\t木\t\t") == [("", 4), ("木foo", 3), ("木", 2), ("", 4)]
