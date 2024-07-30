"""Framework for validating string values"""

from __future__ import annotations

from abc import ABC, abstractmethod


class Restrictor(ABC):
    """Base class for the restriction of values.

    Commonly used in conjunction with the `Input` widget, which accepts a list
    of restrictors via its constructor. The key difference between a Restrictor
    and a Validator is, in the case of the `Input` widget, the new value will
    not appear in the `Input` similar to the behavior of `max_length`.

    To implement your own `Restrictor`, subclass this class.

    Example:
        ```python
        class UppercaseRestrictor(Restrictor):
            def allowed(self, value: str) -> bool:
                return value.isupper()
        ```
    """

    @abstractmethod
    def allowed(self, value: str) -> bool:
        """Tests if the value is allowed or not.

        Args:
            value: The value to test.

        Returns:
            The result of the test.
        """
