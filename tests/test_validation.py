import os
import tempfile

import pytest

from textual.validation import URL, Integer, Number, Path, Regex, String


@pytest.mark.parametrize(
    "value, minimum, maximum, expected_result",
    [
        ("123", None, None, True),  # valid number, no range
        ("-123", None, None, True),  # valid negative number, no range
        ("123.45", None, None, True),  # valid float, no range
        ("1.23e-4", None, None, True),  # valid scientific notation, no range
        ("abc", None, None, False),  # non-numeric string, no range
        ("123", 100, 200, True),  # valid number within range
        ("99", 100, 200, False),  # valid number but not in range
        ("201", 100, 200, False),  # valid number but not in range
        ("1.23e4", 0, 50000, True),  # valid scientific notation within range
    ],
)
def test_Number_validate(value, minimum, maximum, expected_result):
    validator = Number(minimum=minimum, maximum=maximum)
    result = validator.validate(value)
    assert result.valid == expected_result


@pytest.mark.parametrize(
    "regex, value, expected_result",
    [
        (r"\d+", "123", True),  # matches regex for one or more digits
        (r"\d+", "abc", False),  # does not match regex for one or more digits
        (r"[a-z]+", "abc", True),  # matches regex for one or more lowercase letters
        (
            r"[a-z]+",
            "ABC",
            False,
        ),  # does not match regex for one or more lowercase letters
        (r"\w+", "abc123", True),  # matches regex for one or more word characters
        (r"\w+", "!@#", False),  # does not match regex for one or more word characters
    ],
)
def test_RegexValidator_validate(regex, value, expected_result):
    validator = Regex(regex)
    result = validator.validate(value)
    assert result.valid == expected_result


@pytest.mark.parametrize(
    "value, minimum, maximum, expected_result",
    [
        ("123", None, None, True),  # valid integer, no range
        ("-123", None, None, True),  # valid negative integer, no range
        ("123.45", None, None, False),  # float, not a valid integer
        ("1.23e-4", None, None, False),  # scientific notation, not a valid integer
        ("abc", None, None, False),  # non-numeric string, not a valid integer
        ("123", 100, 200, True),  # valid integer within range
        ("99", 100, 200, False),  # valid integer but not in range
        ("201", 100, 200, False),  # valid integer but not in range
        ("1.23e4", None, None, True),  # valid integer in scientific notation
    ],
)
def test_Integer_validate(value, minimum, maximum, expected_result):
    validator = Integer(minimum=minimum, maximum=maximum)
    result = validator.validate(value)
    assert result.valid == expected_result


@pytest.mark.parametrize(
    "value, regex, min_length, max_length, expected_result",
    [
        ("", None, None, None, True),  # empty string
        ("test", None, None, None, True),  # any string with no restrictions
        (
            "test",
            r"\w+",
            None,
            None,
            True,
        ),  # matches regex for one or more word characters
        (
            "test",
            r"\d+",
            None,
            None,
            False,
        ),  # does not match regex for one or more digits
        ("test", None, 5, None, False),  # shorter than minimum length
        ("test", None, None, 3, False),  # longer than maximum length
        ("test", None, 4, 4, True),  # exactly matches minimum and maximum length
        ("test", r"[a-z]+", 2, 6, True),  # matches regex and is within length range
    ],
)
def test_String_validate(value, regex, min_length, max_length, expected_result):
    validator = String(regex=regex, min_length=min_length, max_length=max_length)
    result = validator.validate(value)
    assert result.valid == expected_result


@pytest.mark.parametrize(
    "value, min_length, max_length, expected_result",
    [
        ("http://google.com", None, None, True),  # valid URL
        ("https://google.com", None, None, True),  # valid URL with https
        ("www.google.com", None, None, False),  # missing scheme
        ("https:///path", None, None, False),  # missing netloc
        ("", None, None, False),  # empty string
        ("http://google.com", 20, None, False),  # shorter than minimum length
        ("http://google.com", None, 15, False),  # longer than maximum length
        ("http://google.com", 10, 20, True),  # within length range
        ("://google.com", None, None, False),  # invalid URL (no scheme)
    ],
)
def test_URL_validate(value, min_length, max_length, expected_result):
    validator = URL(min_length=min_length, max_length=max_length)
    result = validator.validate(value)
    assert result.valid == expected_result


@pytest.mark.parametrize(
    "value, exists, min_length, max_length, expected_result",
    [
        (tempfile.gettempdir(), True, None, None, True),  # existing path
        (
            os.path.join(tempfile.gettempdir(), "nonexistent_file"),
            False,
            None,
            None,
            True,
        ),  # non-existing path
        (
            os.path.join(tempfile.gettempdir(), "nonexistent_file"),
            True,
            None,
            None,
            False,
        ),  # non-existing path, but exists=True
        ("", False, None, None, True),  # empty string
        (
            tempfile.gettempdir(),
            False,
            1000,
            None,
            False,
        ),  # shorter than minimum length
        (tempfile.gettempdir(), False, None, 2, False),  # longer than maximum length
        (tempfile.gettempdir(), False, 1, 1000, True),  # within length range
    ],
)
def test_Path_validate(value, exists, min_length, max_length, expected_result):
    validator = Path(exists=exists, min_length=min_length, max_length=max_length)
    result = validator.validate(value)
    assert result.valid == expected_result
