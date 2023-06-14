from fractions import Fraction

import pytest

from textual._resolve import resolve, resolve_fraction_unit
from textual.css.scalar import Scalar
from textual.geometry import Size
from textual.widget import Widget


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


def test_resolve_fraction_unit():
    """Test resolving fraction units in combination with minimum widths."""
    widget1 = Widget()
    widget2 = Widget()
    widget3 = Widget()

    widget1.styles.width = "1fr"
    widget1.styles.min_width = 20

    widget2.styles.width = "2fr"
    widget2.styles.min_width = 10

    widget3.styles.width = "1fr"

    styles = (widget1.styles, widget2.styles, widget3.styles)

    # Try with width 80.
    # Fraction unit should one fourth of width
    assert resolve_fraction_unit(
        styles,
        Size(80, 24),
        Size(80, 24),
        Fraction(80),
        resolve_dimension="width",
    ) == Fraction(20)

    # Try with width 50
    # First widget is fixed at 20
    # Remaining three widgets have 30 to play with
    # Fraction is 10
    assert resolve_fraction_unit(
        styles,
        Size(80, 24),
        Size(80, 24),
        Fraction(50),
        resolve_dimension="width",
    ) == Fraction(10)

    # Try with width 35
    # First widget fixed at 20
    # Fraction is 5
    assert resolve_fraction_unit(
        styles,
        Size(80, 24),
        Size(80, 24),
        Fraction(35),
        resolve_dimension="width",
    ) == Fraction(5)

    # Try with width 32
    # First widget fixed at 20
    # Second widget is fixed at 10
    # Remaining widget has all the space
    # Fraction is 2
    assert resolve_fraction_unit(
        styles,
        Size(80, 24),
        Size(80, 24),
        Fraction(32),
        resolve_dimension="width",
    ) == Fraction(2)


def test_resolve_fraction_unit_stress_test():
    """Check for zero division errors."""
    # https://github.com/Textualize/textual/issues/2673
    widget = Widget()
    styles = widget.styles
    styles.width = "1fr"

    # We're mainly checking for the absence of zero division errors,
    # which is a reoccurring theme for this code.
    for remaining_space in range(1, 101, 10):
        for max_width in range(1, remaining_space):
            styles.max_width = max_width

            for width in range(1, remaining_space):
                resolved_unit = resolve_fraction_unit(
                    [styles, styles, styles],
                    Size(width, 24),
                    Size(width, 24),
                    Fraction(remaining_space),
                    "width",
                )
                assert resolved_unit <= remaining_space


def test_resolve_issue_2502():
    """Test https://github.com/Textualize/textual/issues/2502"""

    widget = Widget()
    widget.styles.width = "1fr"
    widget.styles.min_width = 11

    assert isinstance(
        resolve_fraction_unit(
            (widget.styles,),
            Size(80, 24),
            Size(80, 24),
            Fraction(10),
            resolve_dimension="width",
        ),
        Fraction,
    )
