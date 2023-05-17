"""Framework for validating string values"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from numbers import Number as NumberType
from urllib.parse import urlparse

from textual._types import Pattern, Protocol


@dataclass
class ValidationResult:
    valid: bool
    """True if and only if the value is valid."""
    invalid_reasons: list[str] = field(default_factory=list)
    """A list of reasons why the value was invalid. Empty if valid=True"""

    def __bool__(self):
        return self.valid


class Validation(Protocol):
    """A simple protocol for classes which implement validation of strings."""

    def validate(self, value: str) -> ValidationResult:
        ...


@dataclass
class Regex:
    regex: str | Pattern[str]

    def validate(self, value: str) -> ValidationResult:
        regex = self.regex
        has_match = re.match(regex, value) is not None
        if not has_match:
            invalid_reasons = [
                f"Value {value!r} doesn't match regular expression {regex!r}.",
            ]
            return ValidationResult(valid=False, invalid_reasons=invalid_reasons)
        return ValidationResult(True)


@dataclass
class Number(Regex):
    regex: str | Pattern[str] = r"^-?(0|[1-9]\d*)?(\.\d+)?([eE][-+]?\d+)?$"
    minimum: NumberType | None = None
    """The minimum value of the number, inclusive."""
    maximum: NumberType | None = None
    """The maximum value of the number, exclusive."""

    def validate(self, value: str) -> ValidationResult:
        regex_validation_result = super().validate(value)

        invalid_result = ValidationResult(
            False, [f"Value {value!r} is not a valid number."]
        )
        if not regex_validation_result:
            return invalid_result
        try:
            value = float(value)
        except ValueError:
            return invalid_result
        if not self._validate_range(value):
            minimum = self.minimum
            maximum = self.maximum
            return ValidationResult(
                False,
                [f"Value {value!r} is not in the range {minimum!r} and {maximum!r}."],
            )
        return ValidationResult(True)

    def _validate_range(self, value: NumberType) -> bool:
        if self.minimum is not None and value < self.minimum:
            return False
        if self.maximum is not None and value >= self.maximum:
            return False
        return True


@dataclass
class Integer(Number):
    def validate(self, value: str) -> ValidationResult:
        try:
            value = float(value)
        except ValueError:
            return ValidationResult(False, [f"Value {value!r} is not a valid number."])

        is_integer = value.is_integer()
        if not is_integer:
            return ValidationResult(
                False, [f"Value {value!r} is not a valid integer. "]
            )

        if not self._validate_range(value):
            minimum = self.minimum
            maximum = self.maximum
            return ValidationResult(
                False,
                [f"Value {value!r} is not in the range {minimum!r} and {maximum!r}."],
            )
        return ValidationResult(True)


@dataclass
class String:
    regex: str | Pattern[str] | None = None
    min_length: int | None = None
    max_length: int | None = None

    def validate(self, value: str) -> ValidationResult:
        if self.min_length is not None and len(value) < self.min_length:
            return ValidationResult(
                False,
                [
                    f"Value {value!r} is shorter than minimum length {self.min_length!r}."
                ],
            )

        if self.max_length is not None and len(value) > self.max_length:
            return ValidationResult(
                False,
                [f"Value {value!r} is longer than maximum length {self.max_length!r}."],
            )

        if self.regex is not None:
            regex_result = Regex(self.regex).validate(value)
            if not regex_result:
                return regex_result

        return ValidationResult(True)


@dataclass
class URL(String):
    def validate(self, value: str) -> ValidationResult:
        super_validation_result = super().validate(value)

        if not super_validation_result.valid:
            return super_validation_result

        try:
            parsed_url = urlparse(value)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                return ValidationResult(False, [f"Value {value!r} is not a valid URL."])
        except ValueError:
            return ValidationResult(
                False, [f"Value {value!r} could not be parsed as a URL."]
            )

        return ValidationResult(True)


@dataclass
class Path(String):
    exists: bool = False
    """If True, the path must exist for the validation to pass."""

    def validate(self, value: str) -> ValidationResult:
        super_validation_result = super().validate(value)

        if not super_validation_result.valid:
            return super_validation_result

        if self.exists and not os.path.exists(value):
            return ValidationResult(False, [f"Path {value!r} does not exist."])

        return ValidationResult(True)
