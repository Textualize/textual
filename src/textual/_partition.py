from __future__ import annotations

from typing import Callable, Iterable, TypeVar

T = TypeVar("T")


def partition(
    pred: Callable[[T], object], iterable: Iterable[T]
) -> tuple[list[T], list[T]]:
    """Partition a sequence in to two list from a given predicate. The first list will contain
    the values where the predicate is False, the second list will contain the remaining values.

    Args:
        pred: A callable that returns True or False for a given value.
        iterable: In Iterable of values.

    Returns:
        A list of values where the predicate is False, and a list
            where the predicate is True.
    """

    result: tuple[list[T], list[T]] = ([], [])
    append0 = result[0].append
    append1 = result[1].append

    for value in iterable:
        (append1 if pred(value) else append0)(value)
    return result
