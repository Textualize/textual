import pytest

from textual._box_drawing import combine_quads


@pytest.mark.parametrize(
    "quad1, quad2, expected",
    [
        ((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)),
        ((0, 0, 0, 1), (0, 0, 0, 0), (0, 0, 0, 1)),
        ((0, 0, 0, 1), (0, 0, 0, 1), (0, 0, 0, 1)),
        ((0, 0, 0, 2), (0, 0, 0, 1), (0, 0, 0, 1)),
        ((0, 0, 0, 2), (1, 2, 3, 0), (1, 2, 3, 2)),
        ((0, 1, 0, 2), (1, 0, 3, 0), (1, 1, 3, 2)),
        # Repeating to check cached values
        ((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)),
        ((0, 0, 0, 1), (0, 0, 0, 0), (0, 0, 0, 1)),
        ((0, 0, 0, 1), (0, 0, 0, 1), (0, 0, 0, 1)),
        ((0, 0, 0, 2), (0, 0, 0, 1), (0, 0, 0, 1)),
        ((0, 0, 0, 2), (1, 2, 3, 0), (1, 2, 3, 2)),
        ((0, 1, 0, 2), (1, 0, 3, 0), (1, 1, 3, 2)),
    ],
)
def test_box_combine_quads(quad1, quad2, expected):
    assert combine_quads(quad1, quad2) == expected
