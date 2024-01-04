"""
Utilities to move index-based selections backward/forward.

These utilities concern themselves with selections where not all options are available,
otherwise it would be enough to increment/decrement the index and use the operator `%`
to implement wrapping.
"""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Literal, Protocol, Sequence

from typing_extensions import TypeAlias, TypeVar

if TYPE_CHECKING:
    from .widget import Widget


class Disableable(Protocol):
    """Non-widgets that have an enabled/disabled status."""

    disabled: bool


Direction: TypeAlias = Literal[-1, 1]
"""Valid values to determine navigation direction.

In a vertical setting, 1 points down and -1 points up.
In a horizontal setting, 1 points right and -1 points left.
"""
_D = TypeVar("_D", bound=Disableable)
_W = TypeVar("_W", bound="Widget")


def distance(index: int, start: int, direction: Direction, wrap_at: int) -> int:
    """Computes the distance going from `start` to `index` in the given direction.

    Starting at `start`, this is the number of steps you need to take in the given
    `direction` to reach `index`, assuming there is wrapping at 0 and `wrap_at`.
    This is also the smallest non-negative integer solution `d` to
    `(start + d * direction) % wrap_at == index`.

    The diagram below illustrates the computation of `d1 = distance(2, 8, 1, 10)` and
    `d2 = distance(2, 8, -1, 10)`:

    ```
    start ────────────────────┐
    index ────────┐           │
    indices   0 1 2 3 4 5 6 7 8 9
    d1        2 3 4           0 1
              > > >           > > (direction == 1)
    d2            6 5 4 3 2 1 0
                  < < < < < < <   (direction == -1)
    ```

    Args:
        index: The index that we want to reach.
        start: The starting point to consider when computing the distance.
        direction: The direction in which we want to compute the distance.
        wrap_at: Controls at what point wrapping around takes place.

    Returns:
        The computed distance.
    """
    return direction * (index - start) % wrap_at


def find_first_enabled(candidates: Sequence[_D] | Sequence[_W]) -> int | None:
    """Find the first enabled candidate in a sequence of possibly-disabled objects.

    Args:
        candidates: The sequence of candidates to consider.

    Returns:
        The first enabled candidate or `None` if none were available.
    """
    return next(
        (index for index, candidate in enumerate(candidates) if not candidate.disabled),
        None,
    )


def find_last_enabled(candidates: Sequence[_D] | Sequence[_W]) -> int | None:
    """Find the last enabled candidate in a sequence of possibly-disabled objects.

    Args:
        candidates: The sequence of candidates to consider.

    Returns:
        The last enabled candidate or `None` if none were available.
    """
    total_candidates = len(candidates)
    return next(
        (
            total_candidates - offset_from_end
            for offset_from_end, candidate in enumerate(reversed(candidates), start=1)
            if not candidate.disabled
        ),
        None,
    )


def find_next_enabled(
    candidates: Sequence[_D] | Sequence[_W], anchor: int | None, direction: Direction
) -> int | None:
    """Find the next enabled candidate if we're currently at the given anchor.

    The definition of "next" depends on the given direction and this function will wrap
    around the ends of the sequence of candidates.

    Args:
        candidates: The sequence of candidates to consider.
        anchor: The point of the sequence from which we'll start looking for the next
            candidate.
        direction: The direction in which to traverse the candidates when looking for
            the next available candidate.

    Returns:
        The next enabled candidate. If none are available, return the anchor.
    """

    if anchor is None:
        if candidates:
            return (
                find_first_enabled(candidates)
                if direction == 1
                else find_last_enabled(candidates)
            )
        return None

    key_function = partial(
        distance,
        start=anchor + direction,
        direction=direction,
        wrap_at=len(candidates),
    )
    enabled_candidates = [
        index for index, candidate in enumerate(candidates) if not candidate.disabled
    ]
    return min(enabled_candidates, key=key_function, default=anchor)
