"""Framework for validating string values"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from numbers import Number as NumberType
from typing import Callable
from urllib.parse import urlparse

from textual._types import Pattern


@dataclass
class ValidationResult:
    """The result of calling a `Validator.validate` method."""

    valid: bool
    """True if and only if the value is valid."""
    invalid_reasons: list[InvalidReason] = field(default_factory=list)
    """A list of reasons why the value was invalid. Empty if valid=True"""

    @staticmethod
    def merge(results: list["ValidationResult"]) -> "ValidationResult":
        """Merge multiple ValidationResult objects into one.

        Args:
            results: List of ValidationResult objects to merge.

        Returns:
            Merged ValidationResult object.
        """
        valid = all(result.valid for result in results)
        invalid_reasons = [
            reason for result in results for reason in result.invalid_reasons
        ]
        return ValidationResult(valid=valid, invalid_reasons=invalid_reasons)

    def __bool__(self):
        return self.valid


@dataclass
class InvalidReason:
    value: str | None = None
    """The value which resulted in validation failing."""
    validator: Validator | None = None
    """The Validator which failed."""
    message: str | None = None
    """The description to return, or `None` to use the description returned from
        the `describe_failure` method."""

    def __post_init__(self):
        """Apply the custom description returned from `describe_failure`."""
        if self.message is None and self.validator is not None:
            self.message = self.validator.describe_failure(self)


class Validator(ABC):
    """Implements validation of strings."""

    @abstractmethod
    def validate(self, value: str) -> ValidationResult:
        raise NotImplementedError()

    def describe_failure(self, reason: InvalidReason) -> str | None:
        """Used to provide custom a description for an InvalidReason."""
        return None


@dataclass
class Regex(Validator):
    """A validator that checks that the value matches the supplied regex."""

    regex: str | Pattern[str]
    """The regex pattern to search for."""

    flags: int | re.RegexFlag = 0
    """Flags to pass to `re.search`."""

    class DoesntMatch(InvalidReason):
        pass

    def validate(self, value: str) -> ValidationResult:
        regex = self.regex
        has_match = re.search(regex, value, flags=self.flags) is not None
        if not has_match:
            invalid_reasons = [
                Regex.DoesntMatch(
                    value,
                    validator=self,
                ),
            ]
            return ValidationResult(valid=False, invalid_reasons=invalid_reasons)
        return success()

    def describe_failure(self, reason: InvalidReason) -> str | None:
        return f"Must match regular expression {self.regex!r} (flags={self.flags})."


@dataclass
class Number(Validator):
    """Validator that ensures a number lies within a range."""

    minimum: NumberType | None = None
    """The minimum value of the number, inclusive."""
    maximum: NumberType | None = None
    """The maximum value of the number, inclusive."""

    class NotANumber(InvalidReason):
        pass

    class NotInRange(InvalidReason):
        pass

    def validate(self, value: str) -> ValidationResult:
        try:
            float_value = float(value)
        except ValueError:
            return ValidationResult(False, [Number.NotANumber(value, self)])
        if not self._validate_range(float_value):
            return ValidationResult(
                False,
                [Number.NotInRange(value, self)],
            )
        return success()

    def _validate_range(self, value: NumberType) -> bool:
        if self.minimum is not None and value < self.minimum:
            return False
        if self.maximum is not None and value > self.maximum:
            return False
        return True

    def describe_failure(self, reason: InvalidReason) -> str | None:
        if isinstance(reason, Number.NotANumber):
            return f"Must be a valid number."
        elif isinstance(reason, Number.NotInRange):
            minimum = self.minimum if self.minimum is not None else "-∞"
            maximum = self.maximum if self.maximum is not None else "∞"
            return f"Must be in range [{minimum}, {maximum}]."


@dataclass
class Integer(Number):
    """Validator which ensures the value is an integer which falls within a range."""

    class NotAnInteger(InvalidReason):
        pass

    def validate(self, value: str) -> ValidationResult:
        # First, check that we're dealing with a number in the range.
        number_validation_result = super().validate(value)
        if not number_validation_result:
            return number_validation_result

        # We know it's a number, but is that number an integer?
        is_integer = float(value).is_integer()
        if not is_integer:
            return ValidationResult(False, [Integer.NotAnInteger(value, self)])

        return success()

    def describe_failure(self, reason: InvalidReason) -> str | None:
        if isinstance(reason, Integer.NotAnInteger):
            return f"Must be a valid integer."
        elif isinstance(reason, Integer.NotInRange):
            minimum = self.minimum if self.minimum is not None else "-∞"
            maximum = self.maximum if self.maximum is not None else "∞"
            return f"Must be in range [{minimum}, {maximum}]."
        else:
            return super().describe_failure(reason)


@dataclass
class Length(Validator):
    """Validate that a string is within a range (inclusive)."""

    minimum: int | None = None
    """The inclusive minimum length of the value, or None if unbounded."""

    maximum: int | None = None
    """The inclusive maximum length of the value, or None if unbounded."""

    class TooShort(InvalidReason):
        pass

    class TooLong(InvalidReason):
        pass

    def validate(self, value: str) -> ValidationResult:
        if self.minimum is not None and len(value) < self.minimum:
            return ValidationResult(False, [Length.TooShort(value, self)])

        if self.maximum is not None and len(value) > self.maximum:
            return ValidationResult(False, [Length.TooLong(value, self)])

        return success()

    def describe_failure(self, reason: InvalidReason) -> str | None:
        if isinstance(reason, Length.TooShort):
            return f"Must be {self.minimum} characters or more."
        elif isinstance(reason, Length.TooLong):
            return f"Must be {self.maximum} characters or less."
        else:
            return super().describe_failure(reason)


@dataclass
class Function(Validator):
    """A flexible validator which allows you to provide custom validation logic."""

    function: Callable[[str], bool]
    """Function which takes the value to validate and returns True if valid"""

    failure_description: str
    """The description to use if the function returns False."""

    class ReturnedFalse(InvalidReason):
        pass

    def validate(self, value: str) -> ValidationResult:
        is_valid = self.function(value)
        if is_valid:
            return success()
        return ValidationResult(False, [Function.ReturnedFalse(value, self)])

    def describe_failure(self, reason: InvalidReason) -> str | None:
        return self.failure_description


@dataclass
class URL(Validator):
    """Validator that checks if a URL is valid."""

    class InvalidURL(InvalidReason):
        pass

    def validate(self, value: str) -> ValidationResult:
        invalid_url = ValidationResult(False, [URL.InvalidURL(value, self)])
        try:
            parsed_url = urlparse(value)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                return invalid_url
        except ValueError:
            return invalid_url

        return success()

    def describe_failure(self, reason: InvalidReason) -> str | None:
        return "Must be a valid URL."


def success() -> ValidationResult:
    return ValidationResult(True)


def failure(
    message: str | None = None,
    value: str | None = None,
    validator: Validator | None = None,
) -> ValidationResult:
    return ValidationResult(
        False, [InvalidReason(value=value, validator=validator, message=message)]
    )
