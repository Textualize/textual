from __future__ import annotations

from typing import NamedTuple

import pytest

from textual._layout_resolve import layout_resolve


class Edge(NamedTuple):
    size: int | None = None
    fraction: int = 1
    min_size: int = 1


def test_empty():
    assert layout_resolve(10, []) == []


def test_total_zero():
    assert layout_resolve(0, [Edge(10)]) == [10]


def test_single():
    # One edge fixed size
    assert layout_resolve(100, [Edge(10)]) == [10]
    # One edge fraction of 1
    assert layout_resolve(100, [Edge(None, 1)]) == [100]
    # One edge fraction 3
    assert layout_resolve(100, [Edge(None, 2)]) == [100]
    # One edge, fraction1, min size 20
    assert layout_resolve(100, [Edge(None, 1, 20)]) == [100]
    # One edge fraction 1, min size 120
    assert layout_resolve(100, [Edge(None, 1, 120)]) == [120]


def test_two():
    # Two edges fixed size
    assert layout_resolve(100, [Edge(10), Edge(20)]) == [10, 20]
    # Two edges, fixed size of one exceeds total
    assert layout_resolve(100, [Edge(120), Edge(None, 1)]) == [120, 1]
    # Two edges, fraction 1 each
    assert layout_resolve(100, [Edge(None, 1), Edge(None, 1)]) == [50, 50]
    # Two edges, one with fraction 2, one with fraction 1
    # Note first value is rounded down, second is rounded up
    assert layout_resolve(100, [Edge(None, 2), Edge(None, 1)]) == [66, 34]
    # Two edges, both with fraction 2
    assert layout_resolve(100, [Edge(None, 2), Edge(None, 2)]) == [50, 50]
    # Two edges, one with fraction 3, one with fraction 1
    assert layout_resolve(100, [Edge(None, 3), Edge(None, 1)]) == [75, 25]
    # Two edges, one with fraction 3, one with fraction 1, second with min size of 30
    assert layout_resolve(100, [Edge(None, 3), Edge(None, 1, 30)]) == [70, 30]
    # Two edges, one with fraction 1 and min size 30, one with fraction 3
    assert layout_resolve(100, [Edge(None, 1, 30), Edge(None, 3)]) == [30, 70]


@pytest.mark.parametrize(
    "size, edges, result",
    [
        (10, [Edge(8), Edge(None, 0, 2), Edge(4)], [8, 2, 4]),
        (10, [Edge(None, 1), Edge(None, 1), Edge(None, 1)], [3, 3, 4]),
        (10, [Edge(5), Edge(None, 1), Edge(None, 1)], [5, 2, 3]),
        (10, [Edge(None, 2), Edge(None, 1), Edge(None, 1)], [5, 2, 3]),
        (10, [Edge(None, 2), Edge(3), Edge(None, 1)], [4, 3, 3]),
        (
            10,
            [Edge(None, 2), Edge(None, 1), Edge(None, 1), Edge(None, 1)],
            [4, 2, 2, 2],
        ),
        (
            10,
            [Edge(None, 4), Edge(None, 1), Edge(None, 1), Edge(None, 1)],
            [5, 2, 1, 2],
        ),
        (2, [Edge(None, 1), Edge(None, 1), Edge(None, 1)], [1, 1, 1]),
        (
            2,
            [
                Edge(None, 1, min_size=5),
                Edge(None, 1, min_size=4),
                Edge(None, 1, min_size=3),
            ],
            [5, 4, 3],
        ),
        (
            18,
            [
                Edge(None, 1, min_size=1),
                Edge(3),
                Edge(None, 1, min_size=1),
                Edge(4),
                Edge(None, 1, min_size=1),
                Edge(5),
                Edge(None, 1, min_size=1),
            ],
            [1, 3, 2, 4, 1, 5, 2],
        ),
    ],
)
def test_multiple(size, edges, result):
    assert layout_resolve(size, edges) == result
