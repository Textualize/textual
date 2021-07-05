import pytest

from textual.geometry import clamp, Point, Dimensions, Region


def test_clamp():
    assert clamp(5, 0, 10) == 5
    assert clamp(-1, 0, 10) == 0
    assert clamp(11, 0, 10) == 10
    assert clamp(0, 0, 10) == 0
    assert clamp(10, 0, 10) == 10


def test_point_is_origin():
    assert Point(0, 0).is_origin
    assert not Point(1, 0).is_origin


def test_point_add():
    assert Point(1, 1) + Point(2, 2) == Point(3, 3)
    assert Point(1, 2) + Point(3, 4) == Point(4, 6)
    with pytest.raises(TypeError):
        Point(1, 1) + "foo"


def test_point_sub():
    assert Point(1, 1) - Point(2, 2) == Point(-1, -1)
    assert Point(3, 4) - Point(2, 1) == Point(1, 3)
    with pytest.raises(TypeError):
        Point(1, 1) - "foo"


def test_point_blend():
    assert Point(1, 2).blend(Point(3, 4), 0) == Point(1, 2)
    assert Point(1, 2).blend(Point(3, 4), 1) == Point(3, 4)
    assert Point(1, 2).blend(Point(3, 4), 0.5) == Point(2, 3)
