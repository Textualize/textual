from __future__ import annotations

from typing import TypeVar, Generic

Key = TypeVar("Key")
Value = TypeVar("Value")


class TwoWayDict(Generic[Key, Value]):
    """
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

    def get(self, key: Key, default: Value | None = None) -> Value:
        """Given a key, efficiently lookup and return the associated value.

        Args:
            key: The key
            default: The default return value if not found. Defaults to None.

        Returns:
            The value
        """
        return self._forward.get(key, default)

    def get_key(self, value: Value, default: Key | None = None) -> Key:
        """Given a value, efficiently lookup and return the associated key.

        Args:
            value: The value
            default: The default return value if not found. Defaults to None.

        Returns:
            The key
        """
        return self._reverse.get(value, default)

    def __len__(self):
        return len(self._forward)

    def __contains__(self, item: Key) -> bool:
        return item in self._forward
