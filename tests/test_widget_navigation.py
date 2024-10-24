from __future__ import annotations

import pytest

from textual._widget_navigation import (
    find_first_enabled,
    find_last_enabled,
    find_next_enabled,
    find_next_enabled_no_wrap,
    get_directed_distance,
)


class _D:
    def __init__(self, disabled):
        self.disabled = disabled


# Represent disabled/enabled objects that are compact to write in tests.
D = _D(True)
E = _D(False)


@pytest.mark.parametrize(
    ["index", "start", "direction", "wrap_at", "dist"],
    [
        (2, 8, 1, 10, 4),
        (2, 8, -1, 10, 6),
        (8, 2, -1, 10, 4),
        (8, 2, 1, 10, 6),
        (8, 2, 1, 1234123512, 6),
        (2, 8, 1, 11, 5),
        (2, 8, 1, 12, 6),
        (5, 5, 1, 10, 0),
    ],
)
def test_distance(index, start, direction, wrap_at, dist):
    assert (
        get_directed_distance(
            index=index,
            start=start,
            direction=direction,
            wrap_at=wrap_at,
        )
        == dist
    )


@pytest.mark.parametrize(
    "function",
    [
        find_first_enabled,
        find_last_enabled,
    ],
)
def test_find_enabled_returns_none_on_empty(function):
    assert function([]) is None


@pytest.mark.parametrize(
    ["candidates", "anchor", "direction", "result"],
    [
        # No anchor & no candidates -> no next
        ([], None, 1, None),
        ([], None, -1, None),
        # No anchor but candidates -> get first/last one
        ([E], None, 1, 0),
        ([E, D], None, 1, 0),
        ([E, E], None, 1, 0),
        ([D, E], None, 1, 1),
        ([D, D, E], None, 1, 2),
        ([E], None, -1, 0),
        ([E, E], None, -1, 1),
        ([E, D], None, -1, 0),
        ([E, D, D], None, -1, 0),
        # No enabled candidates -> return the anchor
        ([D, D, D], 0, 1, 0),
        ([D, D, D], 1, 1, 1),
        ([D, D, D], 1, -1, 1),
        ([D, D, D], None, -1, None),
        # General case
        # 0  1  2  3  4  5
        ([E, D, D, E, E, D], 0, 1, 3),
        ([E, D, D, E, E, D], 0, -1, 4),
        ([E, D, D, E, E, D], 1, 1, 3),
        ([E, D, D, E, E, D], 1, -1, 0),
        ([E, D, D, E, E, D], 2, 1, 3),
        ([E, D, D, E, E, D], 2, -1, 0),
        ([E, D, D, E, E, D], 3, 1, 4),
        ([E, D, D, E, E, D], 3, -1, 0),
        ([E, D, D, E, E, D], 4, 1, 0),
        ([E, D, D, E, E, D], 4, -1, 3),
        ([E, D, D, E, E, D], 5, 1, 0),
        ([E, D, D, E, E, D], 5, -1, 4),
    ],
)
def test_find_next_enabled(candidates, anchor, direction, result):
    assert find_next_enabled(candidates, anchor, direction) == result


@pytest.mark.parametrize(
    ["candidates", "anchor", "direction", "result"],
    [
        # No anchor & no candidates -> no next
        ([], None, 1, None),
        ([], None, -1, None),
        # No anchor but candidates -> get first/last one
        ([E], None, 1, 0),
        ([E, D], None, 1, 0),
        ([E, E], None, 1, 0),
        ([D, E], None, 1, 1),
        ([D, D, E], None, 1, 2),
        ([E], None, -1, 0),
        ([E, E], None, -1, 1),
        ([E, D], None, -1, 0),
        ([E, D, D], None, -1, 0),
        # No enabled candidates -> return None
        ([D, D, D], 0, 1, None),
        ([D, D, D], 1, 1, None),
        ([D, D, D], 1, -1, None),
        ([D, D, D], None, -1, None),
        # General case
        # 0  1  2  3  4  5
        ([E, D, D, E, E, D], 0, 1, 3),
        ([E, D, D, E, E, D], 0, -1, None),
        ([E, D, D, E, E, D], 1, 1, 3),
        ([E, D, D, E, E, D], 1, -1, 0),
        ([E, D, D, E, E, D], 2, 1, 3),
        ([E, D, D, E, E, D], 2, -1, 0),
        ([E, D, D, E, E, D], 3, 1, 4),
        ([E, D, D, E, E, D], 3, -1, 0),
        ([E, D, D, E, E, D], 4, 1, None),
        ([E, D, D, E, E, D], 4, -1, 3),
        ([E, D, D, E, E, D], 5, 1, None),
        ([E, D, D, E, E, D], 5, -1, 4),
    ],
)
def test_find_next_enabled_no_wrap(candidates, anchor, direction, result):
    assert find_next_enabled_no_wrap(candidates, anchor, direction) == result


@pytest.mark.parametrize(
    ["function", "start", "direction"],
    [
        (find_next_enabled_no_wrap, 0, 1),
        (find_next_enabled_no_wrap, 0, -1),
        (find_next_enabled_no_wrap, 1, 1),
        (find_next_enabled_no_wrap, 1, -1),
        (find_next_enabled_no_wrap, 2, 1),
        (find_next_enabled_no_wrap, 2, -1),
    ],
)
def test_find_next_with_anchor(function, start, direction):
    assert function([E, E, E], start, direction, True) == start
