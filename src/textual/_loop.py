from __future__ import annotations

from typing import Iterable, Literal, Sequence, TypeVar

T = TypeVar("T")


def loop_first(values: Iterable[T]) -> Iterable[tuple[bool, T]]:
    """Iterate and generate a tuple with a flag for first value."""
    iter_values = iter(values)
    try:
        value = next(iter_values)
    except StopIteration:
        return
    yield True, value
    for value in iter_values:
        yield False, value


def loop_last(values: Iterable[T]) -> Iterable[tuple[bool, T]]:
    """Iterate and generate a tuple with a flag for last value."""
    iter_values = iter(values)
    try:
        previous_value = next(iter_values)
    except StopIteration:
        return
    for value in iter_values:
        yield False, previous_value
        previous_value = value
    yield True, previous_value


def loop_first_last(values: Iterable[T]) -> Iterable[tuple[bool, bool, T]]:
    """Iterate and generate a tuple with a flag for first and last value."""
    iter_values = iter(values)
    try:
        previous_value = next(iter_values)
    except StopIteration:
        return
    first = True
    for value in iter_values:
        yield first, False, previous_value
        first = False
        previous_value = value
    yield first, True, previous_value


def loop_from_index(
    values: Sequence[T],
    index: int,
    direction: Literal[-1, +1] = +1,
    wrap: bool = True,
) -> Iterable[tuple[int, T]]:
    """Iterate over values in a sequence from a given starting index, potentially wrapping the index
    if it would go out of bounds.

    Note that the first value to be yielded is a step from `index`, and `index` will be yielded *last*.


    Args:
        values: A sequence of values.
        index: Starting index.
        direction: Direction to move index (+1 for forward, -1 for backward).
        bool: Should the index wrap when out of bounds?

    Yields:
        A tuple of index and value from the sequence.
    """
    # Sanity check for devs who miss the typing errors
    assert direction in (-1, +1), "direction must be -1 or +1"
    count = len(values)
    if wrap:
        for _ in range(count):
            index = (index + direction) % count
            yield (index, values[index])
    else:
        if direction == +1:
            for _ in range(count):
                if (index := index + 1) >= count:
                    break
                yield (index, values[index])
        else:
            for _ in range(count):
                if (index := index - 1) < 0:
                    break
                yield (index, values[index])
