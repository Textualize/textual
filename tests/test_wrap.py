import pytest

from textual._wrap import chunks, compute_wrap_offsets


@pytest.mark.parametrize(
    "input_text, expected_output",
    [
        ("", []),
        ("    ", [(0, 4, "    ")]),
        ("\t", [(0, 1, "\t")]),
        ("foo", [(0, 3, "foo")]),
        ("  foo  ", [(0, 2, "  "), (2, 7, "foo  ")]),
        ("foo bar", [(0, 4, "foo "), (4, 7, "bar")]),
        ("\tfoo bar", [(0, 1, "\t"), (1, 5, "foo "), (5, 8, "bar")]),
        (" foo bar", [(0, 1, " "), (1, 5, "foo "), (5, 8, "bar")]),
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
        ("", 6, 4, []),
        ("\t", 6, 4, []),
        ("    ", 6, 4, []),
        ("foo bar baz", 6, 4, [4, 8]),
        ("\tfoo bar baz", 6, 4, [1, 5, 9]),
        ("\tfo bar baz", 6, 4, [1, 4, 8]),
        ("\tfo bar baz", 6, 8, [1, 4, 8]),
        ("\tfo bar baz\t", 6, 8, [1, 4, 8]),
        ("\t\t\tfo bar baz\t", 20, 4, [10]),
        ("\t\t\t\t\t\t\t\tfo bar bar", 19, 4, [4, 11]),
        ("\t\t\t\t\t", 19, 4, [4]),
    ],
)
def test_compute_wrap_offsets(text, width, tab_size, expected_output):
    assert compute_wrap_offsets(text, width, tab_size) == expected_output
