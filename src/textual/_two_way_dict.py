from __future__ import annotations

from typing import Generic, TypeVar

Key = TypeVar("Key")
Value = TypeVar("Value")


class TwoWayDict(Generic[Key, Value]):
    """
    A two-way mapping offering O(1) access in both directions.

    Wraps two dictionaries and uses them to provide efficient access to
    both values (given keys) and keys (given values).
    """

    def __init__(self, initial: dict[Key, Value]) -> None:
        self._forward: dict[Key, Value] = initial
        self._reverse: dict[Value, Key] = {value: key for key, value in initial.items()}

    def __setitem__(self, key: Key, value: Value) -> None:
        # TODO: Duplicate values need to be managed to ensure consistency,
        #  decide on best approach.
        self._forward.__setitem__(key, value)
        self._reverse.__setitem__(value, key)

    def __delitem__(self, key: Key) -> None:
        value = self._forward[key]
        self._forward.__delitem__(key)
        self._reverse.__delitem__(value)

    def __iter__(self):
        return iter(self._forward)

    def get(self, key: Key) -> Value | None:
        """Given a key, efficiently lookup and return the associated value.

        Args:
            key: The key

        Returns:
            The value
        """
        return self._forward.get(key)

    def get_key(self, value: Value) -> Key | None:
        """Given a value, efficiently lookup and return the associated key.

        Args:
            value: The value

        Returns:
            The key
        """
        return self._reverse.get(value)

    def contains_value(self, value: Value) -> bool:
        """Check if `value` is a value within this TwoWayDict.

        Args:
            value: The value to check.

        Returns:
            True if the value is within the values of this dict.
        """
        return value in self._reverse

    def __len__(self):
        return len(self._forward)

    def __contains__(self, item: Key) -> bool:
        return item in self._forward
