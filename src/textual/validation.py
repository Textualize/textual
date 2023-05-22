"""Framework for validating string values"""

from __future__ import annotations

import math
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
    failures: list[Failure] = field(default_factory=list)
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
        invalid_reasons = [reason for result in results for reason in result.failures]
        return ValidationResult(valid=valid, failures=invalid_reasons)

    def __bool__(self):
        return self.valid


@dataclass
class Failure:
    """Information about a validation failure."""

    value: str | None = None
    """The value which resulted in validation failing."""
    validator: Validator | None = None
    """The Validator which produced the failure."""
    message: str | None = None
    """An optional override for the message to produce."""

    def __post_init__(self):
        # If a failure message isn't supplied, try to get it from the Validator.
        if self.message is None and self.validator is not None:
            if self.validator.failure_description is not None:
                self.message = self.validator.failure_description
            else:
                self.message = self.validator.describe_failure(self)

    def __rich_repr__(self) -> str:
        yield self.value
        yield self.validator
        yield self.message


class Validator(ABC):
    """Base class for the validation of string values.

    Commonly used in conjunction with the `Input` widget, which accepts a
    list of validators via its constructor. This validation framework can also be used to validate any 'stringly-typed'
    values (for example raw command line input from `sys.args`).

    To implement your own `Validator`, subclass this class.

    Example:
        ```python
        class Palindrome(Validator):
            def validate(self, value: str) -> ValidationResult:
                def is_palindrome(value: str) -> bool:
                    return value == value[::-1]
                return success() if is_palindrome(value) else failure("Not palindrome!")
        ```
    """

    def __init__(self, failure_description: str | None = None):
        self.failure_description = failure_description
        """A description of why the validation failed.

        The description (intended to be user-facing) to attached to the Failure if the validation fails.
        This failure description is ultimately accessible at the time of validation failure  via the `Input.Changed`
        or `Input.Submitted` event, and you can access it on your message handler (a method called, for example,
        `on_input_changed` or a method decorated with `@on(Input.Changed)`.
        """

    @abstractmethod
    def validate(self, value: str) -> ValidationResult:
        """Validate the value and return a ValidationResult describing the outcome of the validation.

        Args:
            value: The value to validate.

        Returns:
            The result of the validation.
        """
        raise NotImplementedError()

    def describe_failure(self, failure: Failure) -> str | None:
        """Return a string description of the Failure.

        Used to provide a more fine-grained description of the failure. A Validator could fail for multiple
        reasons, so this method could be used to provide a different reason for different types of failure.

        Args:
            failure: Information about why the validation failed.

        Returns:
            A string description of the failure.
        """
        return self.failure_description

    def success(self) -> ValidationResult:
        """Shorthand for `ValidationResult(True)`.

        You can return success() from a `Validator.validate` method implementation to signal
        that validation has succeeded.

        Returns:
            A ValidationResult indicating validation succeeded.
        """
        return ValidationResult(True)

    def failure(
        self,
        description: str | None = None,
        value: str | None = None,
        failures: Failure | list[Failure] | None = None,
    ) -> ValidationResult:
        """Shorthand for signaling validation failure.

        You can return failure(...) from a `Validator.validate` implementation to signal validation succeeded.

        Args:
            description: The failure description that will be used. When used in conjunction with the Input widget,
                this is the description that will ultimately be available inside the handler for `Input.Changed`. If not
                supplied, the `failure_description` from the `Validator` will be used. If that is not supplied either,
                then the `describe_failure` method on `Validator` will be called.
            value: The value that was considered invalid. This is optional, and only needs to be supplied if required
                in your `Input.Changed` handler.
            validator: The validator that performed the validation. This is optional, and only needs to be supplied if
                required in your `Input.Changed` handler.
            failures: The reasons the validator failed. If not supplied, a generic `Failure` will be included in the
                ValidationResult returned from this function.

        Returns:
            A ValidationResult representing failed validation, and containing the metadata supplied
                to this function.
        """
        if isinstance(failures, Failure):
            failures = [failures]

        return ValidationResult(
            False,
            failures or [Failure(value=value, validator=self, message=description)],
        )


class Regex(Validator):
    """A validator that the supplied regex is found inside the value (via `re.search`)."""

    def __init__(
        self,
        regex: str | Pattern[str],
        flags: int | re.RegexFlag = 0,
        failure_description: str | None = None,
    ):
        super().__init__(failure_description=failure_description)
        self.regex = regex
        self.flags = flags

    class NoResults(Failure):
        """Indicates validation failed because the regex could not be found within the value string."""

        pass

    def validate(self, value: str) -> ValidationResult:
        """Ensure that the regex is found inside the value.

        Args:
            value: The value to search in.

        Returns:
            The result of the validation.
        """
        regex = self.regex
        has_match = re.search(regex, value, flags=self.flags) is not None
        if not has_match:
            failures = [
                Regex.NoResults(
                    value,
                    validator=self,
                ),
            ]
            return self.failure(failures=failures)
        return self.success()

    def describe_failure(self, failure: Failure) -> str | None:
        """Describes why the validator failed.

        Args:
            failure: Information about why the validation failed.

        Returns:
            A string description of the failure.
        """
        return f"Must match regular expression {self.regex!r} (flags={self.flags})."


class Number(Validator):
    """Validator that ensures the value is a number, with an optional range check."""

    def __init__(
        self,
        minimum: NumberType | None = None,
        maximum: NumberType | None = None,
        failure_description: str | None = None,
    ):
        super().__init__(failure_description=failure_description)
        self.minimum = minimum
        """The minimum value of the number, inclusive. If `None`, the minimum is unbounded."""
        self.maximum = maximum
        """The maximum value of the number, inclusive. If `None`, the maximum is unbounded."""

    class NotANumber(Failure):
        """Indicates a failure due to the value not being a valid number (decimal/integer, inc. scientific notation)"""

        pass

    class NotInRange(Failure):
        """Indicates a failure due to the number not being within the range [minimum, maximum]."""

        pass

    def validate(self, value: str) -> ValidationResult:
        """Ensure that `value` is a valid number, optionally within a range.

        Args:
            value: The value to validate.

        Returns:
            The result of the validation.
        """
        try:
            float_value = float(value)
        except ValueError:
            return ValidationResult(False, [Number.NotANumber(value, self)])

        if float_value in {math.nan, math.inf, -math.inf}:
            return ValidationResult(False, [Number.NotANumber(value, self)])

        if not self._validate_range(float_value):
            return ValidationResult(
                False,
                [Number.NotInRange(value, self)],
            )
        return self.success()

    def _validate_range(self, value: NumberType) -> bool:
        """Return a boolean indicating whether the number is within the range specified in the attributes."""
        if self.minimum is not None and value < self.minimum:
            return False
        if self.maximum is not None and value > self.maximum:
            return False
        return True

    def describe_failure(self, failure: Failure) -> str | None:
        """Describes why the validator failed.

        Args:
            failure: Information about why the validation failed.

        Returns:
            A string description of the failure.
        """
        if isinstance(failure, Number.NotANumber):
            return f"Must be a valid number."
        elif isinstance(failure, Number.NotInRange):
            minimum = self.minimum if self.minimum is not None else "-∞"
            maximum = self.maximum if self.maximum is not None else "∞"
            return f"Must be in range [{minimum}, {maximum}]."
        else:
            return super().describe_failure(failure)


class Integer(Number):
    """Validator which ensures the value is an integer which falls within a range."""

    class NotAnInteger(Failure):
        """Indicates a failure due to the value not being a valid integer."""

        pass

    def validate(self, value: str) -> ValidationResult:
        """Ensure that `value` is an integer, optionally within a range.

        Args:
            value: The value to validate.

        Returns:
            The result of the validation.
        """
        # First, check that we're dealing with a number in the range.
        number_validation_result = super().validate(value)
        if not number_validation_result:
            return number_validation_result

        # We know it's a number, but is that number an integer?
        is_integer = float(value).is_integer()
        if not is_integer:
            return ValidationResult(False, [Integer.NotAnInteger(value, self)])

        return self.success()

    def describe_failure(self, failure: Failure) -> str | None:
        """Describes why the validator failed.

        Args:
            failure: Information about why the validation failed.

        Returns:
            A string description of the failure.
        """
        if isinstance(failure, Integer.NotAnInteger):
            return f"Must be a valid integer."
        elif isinstance(failure, Integer.NotInRange):
            minimum = self.minimum if self.minimum is not None else "-∞"
            maximum = self.maximum if self.maximum is not None else "∞"
            return f"Must be in range [{minimum}, {maximum}]."
        else:
            return super().describe_failure(failure)


class Length(Validator):
    """Validate that a string is within a range (inclusive)."""

    def __init__(
        self,
        minimum: int | None = None,
        maximum: int | None = None,
        failure_description: str | None = None,
    ):
        super().__init__(failure_description=failure_description)
        self.minimum = minimum
        """The inclusive minimum length of the value, or None if unbounded."""
        self.maximum = maximum
        """The inclusive maximum length of the value, or None if unbounded."""

    class TooShort(Failure):
        """Indicates a failure due to the value being too short."""

        pass

    class TooLong(Failure):
        """Indicates a failure due to a value being too long."""

        pass

    def validate(self, value: str) -> ValidationResult:
        """Ensure that value falls within the maximum and minimum length constraints.

        Args:
            value: The value to validate.

        Returns:
            The result of the validation.
        """
        if self.minimum is not None and len(value) < self.minimum:
            return ValidationResult(False, [Length.TooShort(value, self)])

        if self.maximum is not None and len(value) > self.maximum:
            return ValidationResult(False, [Length.TooLong(value, self)])

        return self.success()

    def describe_failure(self, failure: Failure) -> str | None:
        """Describes why the validator failed.

        Args:
            failure: Information about why the validation failed.

        Returns:
            A string description of the failure.
        """
        if isinstance(failure, Length.TooShort):
            return f"Must be {self.minimum} characters or more."
        elif isinstance(failure, Length.TooLong):
            return f"Must be {self.maximum} characters or less."
        else:
            return super().describe_failure(failure)


@dataclass
class Function(Validator):
    """A flexible validator which allows you to provide custom validation logic."""

    function: Callable[[str], bool]
    """Function which takes the value to validate and returns True if valid, and False otherwise."""

    class ReturnedFalse(Failure):
        """Indicates validation failed because the supplied function returned False."""

        pass

    def validate(self, value: str) -> ValidationResult:
        """Validate that the supplied function returns True.

        Args:
            value: The value to pass into the supplied function.

        Returns:
            A ValidationResult indicating success if the function returned True,
                and failure if the function return False.
        """
        is_valid = self.function(value)
        if is_valid:
            return self.success()
        return self.failure(failures=Function.ReturnedFalse(value, self))

    def describe_failure(self, failure: Failure) -> str | None:
        """Describes why the validator failed.

        Args:
            failure: Information about why the validation failed.

        Returns:
            A string description of the failure.
        """
        return self.failure_description


class URL(Validator):
    """Validator that checks if a URL is valid (ensuring a scheme is present)."""

    class InvalidURL(Failure):
        """Indicates that the URL is not valid."""

        pass

    def validate(self, value: str) -> ValidationResult:
        """Validates that `value` is a valid URL (contains a scheme).

        Args:
            value: The value to validate.

        Returns:
            The result of the validation.
        """
        invalid_url = ValidationResult(False, [URL.InvalidURL(value, self)])
        try:
            parsed_url = urlparse(value)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                return invalid_url
        except ValueError:
            return invalid_url

        return self.success()

    def describe_failure(self, failure: Failure) -> str | None:
        """Describes why the validator failed.

        Args:
            failure: Information about why the validation failed.

        Returns:
            A string description of the failure.
        """
        return "Must be a valid URL."
