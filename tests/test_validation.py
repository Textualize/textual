import pytest

from textual.validation import URL, Integer, Length, Number, Regex


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
def test_Regex_validate(regex, value, expected_result):
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
    "value, min_length, max_length, expected_result",
    [
        ("", None, None, True),  # empty string
        ("test", None, None, True),  # any string with no restrictions
        ("test", 5, None, False),  # shorter than minimum length
        ("test", None, 3, False),  # longer than maximum length
        ("test", 4, 4, True),  # exactly matches minimum and maximum length
        ("test", 2, 6, True),  # within length range
    ],
)
def test_Length_validate(value, min_length, max_length, expected_result):
    validator = Length(minimum=min_length, maximum=max_length)
    result = validator.validate(value)
    assert result.valid == expected_result


@pytest.mark.parametrize(
    "value, expected_result",
    [
        ("http://google.com", True),  # valid URL
        ("https://google.com", True),  # valid URL with https
        ("www.google.com", False),  # missing scheme
        ("://google.com", False),  # invalid URL (no scheme)
        ("https:///path", False),  # missing netloc
        ("", False),  # empty string
    ],
)
def test_URL_validate(value, expected_result):
    validator = URL()
    result = validator.validate(value)
    assert result.valid == expected_result
