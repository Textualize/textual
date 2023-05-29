from __future__ import annotations

import pytest

from textual.validation import (
    URL,
    Failure,
    Function,
    Integer,
    Length,
    Number,
    Regex,
    ValidationResult,
    Validator,
)

VALIDATOR = Function(lambda value: True)


def test_ValidationResult_merge_successes():
    results = [ValidationResult.success(), ValidationResult.success()]
    assert ValidationResult.merge(results) == ValidationResult.success()


def test_ValidationResult_merge_failures():
    failure_one = Failure(VALIDATOR, "1")
    failure_two = Failure(VALIDATOR, "2")
    results = [
        ValidationResult.failure([failure_one]),
        ValidationResult.failure([failure_two]),
        ValidationResult.success(),
    ]
    expected_result = ValidationResult.failure([failure_one, failure_two])
    assert ValidationResult.merge(results) == expected_result


def test_ValidationResult_failure_descriptions():
    result = ValidationResult.failure(
        [
            Failure(VALIDATOR, description="One"),
            Failure(VALIDATOR, description="Two"),
            Failure(VALIDATOR, description="Three"),
        ],
    )
    assert result.failure_descriptions == ["One", "Two", "Three"]


class ValidatorWithDescribeFailure(Validator):
    def validate(self, value: str) -> ValidationResult:
        return self.failure()

    def describe_failure(self, failure: Failure) -> str | None:
        return "describe_failure"


def test_Failure_description_priorities_parameter_only():
    number_validator = Number(failure_description="ABC")
    non_number_value = "x"
    result = number_validator.validate(non_number_value)
    # The inline value takes priority over the describe_failure.
    assert result.failures[0].description == "ABC"


def test_Failure_description_priorities_parameter_and_describe_failure():
    validator = ValidatorWithDescribeFailure(failure_description="ABC")
    result = validator.validate("x")
    # Even though the validator has a `describe_failure`, we've provided it
    # inline and the inline value should take priority.
    assert result.failures[0].description == "ABC"


def test_Failure_description_priorities_describe_failure_only():
    validator = ValidatorWithDescribeFailure()
    result = validator.validate("x")
    assert result.failures[0].description == "describe_failure"


class ValidatorWithFailureMessageAndNoDescribe(Validator):
    def validate(self, value: str) -> ValidationResult:
        return self.failure(description="ABC")


def test_Failure_description_parameter_and_description_inside_validate():
    validator = ValidatorWithFailureMessageAndNoDescribe()
    result = validator.validate("x")
    assert result.failures[0].description == "ABC"


class ValidatorWithFailureMessageAndDescribe(Validator):
    def validate(self, value: str) -> ValidationResult:
        return self.failure(value=value, description="ABC")

    def describe_failure(self, failure: Failure) -> str | None:
        return "describe_failure"


def test_Failure_description_describe_and_description_inside_validate():
    # This is kind of a weird case - there's no reason to supply both of
    # these but lets still make sure we're sensible about how we handle it.
    validator = ValidatorWithFailureMessageAndDescribe()
    result = validator.validate("x")
    assert result.failures == [Failure(validator, "x", "ABC")]


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
    assert result.is_valid == expected_result


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
    assert result.is_valid == expected_result


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
    assert result.is_valid == expected_result


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
    assert result.is_valid == expected_result


@pytest.mark.parametrize(
    "value, expected_result",
    [
        ("http://example.com", True),  # valid URL
        ("https://example.com", True),  # valid URL with https
        ("www.example.com", False),  # missing scheme
        ("://example.com", False),  # invalid URL (no scheme)
        ("https:///path", False),  # missing netloc
        (
            "redis://username:pass[word@localhost:6379/0",
            False,
        ),  # invalid URL characters
        ("", False),  # empty string
    ],
)
def test_URL_validate(value, expected_result):
    validator = URL()
    result = validator.validate(value)
    assert result.is_valid == expected_result


@pytest.mark.parametrize(
    "function, failure_description, is_valid",
    [
        ((lambda value: True), None, True),
        ((lambda value: False), "failure!", False),
    ],
)
def test_Function_validate(function, failure_description, is_valid):
    validator = Function(function, failure_description)
    result = validator.validate("x")
    assert result.is_valid is is_valid
    if result.failure_descriptions:
        assert result.failure_descriptions[0] == failure_description
