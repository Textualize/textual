import pytest

from textual._resolve import resolve
from textual.css.scalar import Scalar
from textual.geometry import Size


def test_resolve_empty():
    assert resolve([], 10, 1, Size(20, 10), Size(80, 24)) == []


@pytest.mark.parametrize(
    "scalars,total,gutter,result",
    [
        (["10"], 100, 0, [(0, 10)]),
        (
            ["10", "20"],
            100,
            0,
            [(0, 10), (10, 20)],
        ),
        (
            ["10", "20"],
            100,
            1,
            [(0, 10), (11, 20)],
        ),
        (
            ["10", "1fr"],
            100,
            1,
            [(0, 10), (11, 89)],
        ),
        (
            ["1fr", "1fr"],
            100,
            0,
            [(0, 50), (50, 50)],
        ),
        (
            ["3", "1fr", "1fr", "1"],
            100,
            1,
            [(0, 3), (4, 46), (51, 47), (99, 1)],
        ),
    ],
)
def test_resolve(scalars, total, gutter, result):
    assert (
        resolve(
            [Scalar.parse(scalar) for scalar in scalars],
            total,
            gutter,
            Size(40, 20),
            Size(80, 24),
        )
        == result
    )
