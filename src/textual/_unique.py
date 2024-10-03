"""A utility function to de-duplicate iterables while preserving order."""

from __future__ import annotations

from itertools import chain
from typing import Iterable, TypeVar

T = TypeVar("T")


def unique_ordered(*widgets: Iterable[T]) -> list[T]:
    """Converts a number of iterables of an object in to a list
    where each value appears only once, while preserving order."""
    unique_objects = list(dict.fromkeys(chain(*widgets)))
    return unique_objects
