import pytest

from textual.expand_tabs import expand_tabs_inline


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
