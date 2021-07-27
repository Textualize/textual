import pytest

from textual.geometry import clamp, Point, Dimensions, Region


def test_dimensions_region():
    assert Dimensions(30, 40).region == Region(0, 0, 30, 40)


def test_dimensions_contains():
    assert Dimensions(10, 10).contains(5, 5)
    assert Dimensions(10, 10).contains(9, 9)
    assert Dimensions(10, 10).contains(0, 0)
    assert not Dimensions(10, 10).contains(10, 9)
    assert not Dimensions(10, 10).contains(9, 10)
    assert not Dimensions(10, 10).contains(-1, 0)
    assert not Dimensions(10, 10).contains(0, -1)


def test_dimensions_contains_point():
    assert Dimensions(10, 10).contains_point(Point(5, 5))
    assert Dimensions(10, 10).contains_point(Point(9, 9))
    assert Dimensions(10, 10).contains_point(Point(0, 0))
    assert not Dimensions(10, 10).contains_point(Point(10, 9))
    assert not Dimensions(10, 10).contains_point(Point(9, 10))
    assert not Dimensions(10, 10).contains_point(Point(-1, 0))
    assert not Dimensions(10, 10).contains_point(Point(0, -1))


def test_dimensions_contains_special():
    with pytest.raises(TypeError):
        (1, 2, 3) in Dimensions(10, 10)

    assert (5, 5) in Dimensions(10, 10)
    assert (9, 9) in Dimensions(10, 10)
    assert (0, 0) in Dimensions(10, 10)
    assert (10, 9) not in Dimensions(10, 10)
    assert (9, 10) not in Dimensions(10, 10)
    assert (-1, 0) not in Dimensions(10, 10)
    assert (0, -1) not in Dimensions(10, 10)


def test_dimensions_bool():
    assert Dimensions(1, 1)
    assert Dimensions(3, 4)
    assert not Dimensions(0, 1)
    assert not Dimensions(1, 0)


def test_dimensions_area():
    assert Dimensions(0, 0).area == 0
    assert Dimensions(1, 0).area == 0
    assert Dimensions(1, 1).area == 1
    assert Dimensions(4, 5).area == 20


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


def test_region_from_origin():
    assert Region.from_origin(Point(3, 4), (5, 6)) == Region(3, 4, 5, 6)


def test_region_area():
    assert Region(3, 4, 0, 0).area == 0
    assert Region(3, 4, 5, 6).area == 30


def test_region_size():
    assert isinstance(Region(3, 4, 5, 6).size, Dimensions)
    assert Region(3, 4, 5, 6).size == Dimensions(5, 6)


def test_region_origin():
    assert Region(1, 2, 3, 4).origin == Point(1, 2)


def test_region_add():
    assert Region(1, 2, 3, 4) + (10, 20) == Region(11, 22, 3, 4)
    with pytest.raises(TypeError):
        Region(1, 2, 3, 4) + "foo"


def test_region_sub():
    assert Region(11, 22, 3, 4) - (10, 20) == Region(1, 2, 3, 4)
    with pytest.raises(TypeError):
        Region(1, 2, 3, 4) - "foo"


def test_region_overlaps():
    assert Region(10, 10, 30, 20).overlaps(Region(0, 0, 20, 20))
    assert not Region(10, 10, 5, 5).overlaps(Region(15, 15, 20, 20))

    assert not Region(10, 10, 5, 5).overlaps(Region(0, 0, 50, 10))
    assert Region(10, 10, 5, 5).overlaps(Region(0, 0, 50, 11))
    assert not Region(10, 10, 5, 5).overlaps(Region(0, 15, 50, 10))
    assert Region(10, 10, 5, 5).overlaps(Region(0, 14, 50, 10))


def test_region_contains():
    assert Region(10, 10, 20, 30).contains(10, 10)
    assert Region(10, 10, 20, 30).contains(29, 39)
    assert not Region(10, 10, 20, 30).contains(30, 40)


def test_region_contains_point():
    assert Region(10, 10, 20, 30).contains_point((10, 10))
    assert Region(10, 10, 20, 30).contains_point((29, 39))
    assert not Region(10, 10, 20, 30).contains_point((30, 40))
    with pytest.raises(TypeError):
        Region(10, 10, 20, 30).contains_point((1, 2, 3))


def test_region_contains_region():
    assert Region(10, 10, 20, 30).contains_region(Region(10, 10, 5, 5))
    assert not Region(10, 10, 20, 30).contains_region(Region(10, 9, 5, 5))
    assert not Region(10, 10, 20, 30).contains_region(Region(9, 10, 5, 5))
    assert Region(10, 10, 20, 30).contains_region(Region(10, 10, 20, 30))
    assert not Region(10, 10, 20, 30).contains_region(Region(10, 10, 21, 30))
    assert not Region(10, 10, 20, 30).contains_region(Region(10, 10, 20, 31))


def test_region_translate():
    assert Region(1, 2, 3, 4).translate(10, 20) == Region(11, 22, 3, 4)
    assert Region(1, 2, 3, 4).translate(y=20) == Region(1, 22, 3, 4)


def test_region_contains_special():
    assert (10, 10) in Region(10, 10, 20, 30)
    assert (9, 10) not in Region(10, 10, 20, 30)
    assert Region(10, 10, 5, 5) in Region(10, 10, 20, 30)
    assert Region(5, 5, 5, 5) not in Region(10, 10, 20, 30)
    assert "foo" not in Region(0, 0, 10, 10)


def test_clip():
    assert Region(10, 10, 20, 30).clip(20, 25) == Region(10, 10, 10, 15)


def test_region_intersection():
    assert Region(0, 0, 100, 50).intersection(Region(10, 10, 10, 10)) == Region(
        10, 10, 10, 10
    )
    assert Region(10, 10, 30, 20).intersection(Region(20, 15, 60, 40)) == Region(
        20, 15, 20, 15
    )

    assert not Region(10, 10, 20, 30).intersection(Region(50, 50, 100, 200))
