"""Provides collection-based utility code."""

from __future__ import annotations
from typing import Generic, TypeVar, Iterator, overload, Iterable

T = TypeVar("T")


class ImmutableSequence(Generic[T]):
    """Class to wrap a sequence of some sort, but not allow modification."""

    def __init__(self, wrap: Iterable[T]) -> None:
        """Initialise the immutable sequence.

        Args:
            wrap (Iterable[T]): The iterable value being wrapped.
        """
        self._list = list(wrap)

    @overload
    def __getitem__(self, index: int) -> T:
        ...

    @overload
    def __getitem__(self, index: slice) -> ImmutableSequence[T]:
        ...

    def __getitem__(self, index: int | slice) -> T | ImmutableSequence[T]:
        return (
            self._list[index]
            if isinstance(index, int)
            else ImmutableSequence[T](self._list[index])
        )

    def __iter__(self) -> Iterator[T]:
        return iter(self._list)

    def __len__(self) -> int:
        return len(self._list)

    def __length_hint__(self) -> int:
        return len(self)

    def __bool__(self) -> bool:
        return bool(self._list)

    def __contains__(self, item: T) -> bool:
        return item in self._list

    def index(self, item: T) -> int:
        """Return the index of the given item.

        Args:
            item (T): The item to find in the sequence.

        Returns:
            int: The index of the item in the sequence.

        Raises:
            ValueError: If the item is not in the sequence.
        """
        return self._list.index(item)

    def __reversed__(self) -> Iterator[T]:
        return reversed(self._list)
