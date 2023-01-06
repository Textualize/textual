"""Provides an immutable sequence view class."""

from __future__ import annotations
from typing import Generic, TypeVar, Iterator, overload, Sequence

T = TypeVar("T")


class ImmutableSequenceView(Generic[T]):
    """Class to wrap a sequence of some sort, but not allow modification."""

    def __init__(self, wrap: Sequence[T]) -> None:
        """Initialise the immutable sequence.

        Args:
            wrap (Sequence[T]): The sequence being wrapped.
        """
        self._wrap = wrap

    @overload
    def __getitem__(self, index: int) -> T:
        ...

    @overload
    def __getitem__(self, index: slice) -> ImmutableSequenceView[T]:
        ...

    def __getitem__(self, index: int | slice) -> T | ImmutableSequenceView[T]:
        return (
            self._wrap[index]
            if isinstance(index, int)
            else ImmutableSequenceView[T](self._wrap[index])
        )

    def __iter__(self) -> Iterator[T]:
        return iter(self._wrap)

    def __len__(self) -> int:
        return len(self._wrap)

    def __length_hint__(self) -> int:
        return len(self)

    def __bool__(self) -> bool:
        return bool(self._wrap)

    def __contains__(self, item: T) -> bool:
        return item in self._wrap

    def index(self, item: T) -> int:
        """Return the index of the given item.

        Args:
            item (T): The item to find in the sequence.

        Returns:
            T: The index of the item in the sequence.

        Raises:
            ValueError: If the item is not in the sequence.
        """
        return self._wrap.index(item)

    def __reversed__(self) -> Iterator[T]:
        return reversed(self._wrap)
