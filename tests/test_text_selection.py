"""Tests for the text selection helpers."""

import re
from contextlib import contextmanager

import pytest

from textual._text_selection import (
    _flat_offset_to_offset,
    _split_lines,
    get_paragraph_offsets,
    get_paragraph_selection,
    get_word_selection,
)
from textual import _word_segmentation
from textual._word_segmentation import get_word_offsets
from textual.geometry import Offset
from textual.selection import Selection


@contextmanager
def _re_fallback():
    """Temporarily force the word-segmentation module to use the standard re fallback."""
    original_regex_module = _word_segmentation._regex_module
    original_word_re = _word_segmentation._WORD_OR_URL_RE
    _word_segmentation._regex_module = None
    _word_segmentation._WORD_OR_URL_RE = re.compile(
        r"(?:https?|ftp)://\S+|[\w'’-]+",
        re.UNICODE,
    )
    try:
        yield
    finally:
        _word_segmentation._regex_module = original_regex_module
        _word_segmentation._WORD_OR_URL_RE = original_word_re


@pytest.mark.parametrize(
    "text,offset,expected",
    [
        ("hello world", 0, (0, 5)),
        ("hello world", 3, (0, 5)),
        ("hello world", 6, (6, 11)),
        ("hello world", 9, (6, 11)),
        ("hello world", 10, (6, 11)),
        ("hello world", 11, (6, 11)),
        ("hello world", 15, None),
        ("", 0, None),
    ],
)
def test_get_word_offsets(text, offset, expected):
    assert get_word_offsets(text, offset) == expected


def test_get_word_offsets_url():
    text = "Visit https://example.com/path for info."
    start = text.index("https")
    for offset in range(start, len(text)):
        if text[offset].isspace():
            break
        assert get_word_offsets(text, offset) == (
            start,
            start + len("https://example.com/path"),
        )


@pytest.mark.skipif(
    _word_segmentation._regex_module is None,
    reason="regex package not installed",
)
def test_get_word_offsets_unicode_combining_mark():
    """When regex is available, combining marks stay attached to the word."""
    # "café" spelled with a combining acute accent (e + U+0301).
    text = "cafe\u0301"
    assert get_word_offsets(text, 2) == (0, 5)


def test_get_word_offsets_re_fallback():
    """The re fallback still handles basic words correctly."""
    with _re_fallback():
        assert get_word_offsets("hello world", 0) == (0, 5)
        assert get_word_offsets("hello world", 6) == (6, 11)


def test_get_word_offsets_url_re_fallback():
    """The re fallback still selects URLs."""
    with _re_fallback():
        text = "Visit https://example.com/path for info."
        start = text.index("https")
        for offset in range(start, len(text)):
            if text[offset].isspace():
                break
            assert get_word_offsets(text, offset) == (
                start,
                start + len("https://example.com/path"),
            )


def test_get_word_selection():
    text = "hello world\nfoo bar"
    selection = get_word_selection(text, Offset(8, 0))  # on "world"
    assert selection == Selection.from_offsets(Offset(6, 0), Offset(11, 0))


def test_get_word_selection_multiline():
    text = "hello world\nfoo bar"
    selection = get_word_selection(text, Offset(2, 1))  # on "foo"
    assert selection == Selection.from_offsets(Offset(0, 1), Offset(3, 1))


def test_get_word_selection_crlf():
    text = "hello world\r\nfoo bar"
    selection = get_word_selection(text, Offset(2, 1))  # on "foo"
    assert selection == Selection.from_offsets(Offset(0, 1), Offset(3, 1))


def test_get_word_selection_inside_crlf_newline():
    """Clicking inside a CRLF newline should still select the preceding word."""
    text = "hello world\r\nfoo bar"
    # Offset(10, 0) is the last character of "world" on the first line.
    selection = get_word_selection(text, Offset(10, 0))
    assert selection == Selection.from_offsets(Offset(6, 0), Offset(11, 0))


def test_flat_offset_to_offset():
    assert _flat_offset_to_offset("hello\nworld", 0) == Offset(0, 0)
    assert _flat_offset_to_offset("hello\nworld", 6) == Offset(0, 1)
    assert _flat_offset_to_offset("hello\nworld", 8) == Offset(2, 1)
    assert _flat_offset_to_offset("hello\nworld", 20) == Offset(5, 1)


def test_flat_offset_to_offset_crlf():
    assert _flat_offset_to_offset("hello\r\nworld", 0) == Offset(0, 0)
    assert _flat_offset_to_offset("hello\r\nworld", 5) == Offset(5, 0)
    assert _flat_offset_to_offset("hello\r\nworld", 7) == Offset(0, 1)
    assert _flat_offset_to_offset("hello\r\nworld", 9) == Offset(2, 1)
    assert _flat_offset_to_offset("hello\r\nworld", 20) == Offset(5, 1)


def test_split_lines():
    assert _split_lines("hello\nworld") == [("hello", 1), ("world", 0)]
    assert _split_lines("hello\r\nworld") == [("hello", 2), ("world", 0)]
    assert _split_lines("hello\nworld\n") == [("hello", 1), ("world", 1)]
    assert _split_lines("\n\n") == [("", 1), ("", 1)]
    assert _split_lines("") == []


@pytest.mark.parametrize(
    "text,offset,expected",
    [
        ("para1\n\npara2\n\npara3", 2, (0, 5)),
        ("para1\n\npara2\n\npara3", 8, (7, 12)),
        ("para1\n\npara2\n\npara3", 14, (14, 19)),
        ("line1\nline2\n\npara2", 1, (0, 11)),
        ("line1\nline2\n\npara2", 8, (0, 11)),
        ("single", 3, (0, 6)),
        ("", 0, None),
    ],
)
def test_get_paragraph_offsets(text, offset, expected):
    assert get_paragraph_offsets(text, offset) == expected


def test_get_paragraph_offsets_crlf():
    text = "para1\r\n\r\npara2\r\n\r\npara3"
    assert get_paragraph_offsets(text, 2) == (0, 5)
    assert get_paragraph_offsets(text, 10) == (9, 14)
    assert get_paragraph_offsets(text, 18) == (18, 23)


def test_get_paragraph_selection():
    text = "para1\n\npara2\n\npara3"
    selection = get_paragraph_selection(text, Offset(2, 2))
    assert selection == Selection.from_offsets(Offset(0, 2), Offset(5, 2))


def test_get_paragraph_selection_crlf():
    text = "para1\r\n\r\npara2\r\n\r\npara3"
    selection = get_paragraph_selection(text, Offset(2, 2))
    assert selection == Selection.from_offsets(Offset(0, 2), Offset(5, 2))
