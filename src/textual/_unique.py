"""A utility function to de-duplicate iterables while preserving order."""

from __future__ import annotations

from itertools import chain
from typing import Iterable, TypeVar

T = TypeVar("T")


def unique_ordered(*values: Iterable[T]) -> list[T]:
    """Converts a number of iterables of an object in to a list
    where each value appears only once, while preserving order.

    Args:
        *values: A number of iterables of values to make unique.

    Returns:
        A list of values, where each value appears exactly once, in the order they were given.

    """
    unique_objects = list(dict.fromkeys(chain.from_iterable(values)))
    return unique_objects
