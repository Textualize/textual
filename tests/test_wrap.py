import pytest

from textual._wrap import chunks, divide_line


@pytest.mark.parametrize(
    "input_text, expected_output",
    [
        ("", []),
        ("    ", [(0, 4, "    ")]),
        ("\t", [(0, 1, "\t")]),
        ("foo", [(0, 3, "foo")]),
        ("  foo  ", [(0, 7, "  foo  ")]),
        ("foo bar", [(0, 4, "foo "), (4, 7, "bar")]),
        ("\tfoo bar", [(0, 5, "\tfoo "), (5, 8, "bar")]),
        (" foo bar", [(0, 5, " foo "), (5, 8, "bar")]),
        ("foo bar   ", [(0, 4, "foo "), (4, 10, "bar   ")]),
        ("foo\t  bar   ", [(0, 6, "foo\t  "), (6, 12, "bar   ")]),
        ("木\t  川   ", [(0, 4, "木\t  "), (4, 8, "川   ")]),
    ],
)
def test_chunks(input_text, expected_output):
    assert list(chunks(input_text)) == expected_output


@pytest.mark.parametrize(
    "text, width, tab_size, expected_output",
    [
        ("foo bar baz", 6, 4, [4, 8]),
        ("\tfoo bar baz", 6, 4, [3, 9]),
        ("\tfo bar baz", 6, 4, [3, 8]),
        ("\tfo bar baz", 6, 8, [1, 4, 8]),
    ],
)
def test_divide_line(text, width, tab_size, expected_output):
    assert divide_line(text, width, tab_size) == expected_output
