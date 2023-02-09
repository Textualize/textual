import pytest

from textual.geometry import Offset, Region, Size, Spacing, clamp


def test_dimensions_region():
    assert Size(30, 40).region == Region(0, 0, 30, 40)


def test_dimensions_contains():
    assert Size(10, 10).contains(5, 5)
    assert Size(10, 10).contains(9, 9)
    assert Size(10, 10).contains(0, 0)
    assert not Size(10, 10).contains(10, 9)
    assert not Size(10, 10).contains(9, 10)
    assert not Size(10, 10).contains(-1, 0)
    assert not Size(10, 10).contains(0, -1)


def test_dimensions_contains_point():
    assert Size(10, 10).contains_point(Offset(5, 5))
    assert Size(10, 10).contains_point(Offset(9, 9))
    assert Size(10, 10).contains_point(Offset(0, 0))
    assert not Size(10, 10).contains_point(Offset(10, 9))
    assert not Size(10, 10).contains_point(Offset(9, 10))
    assert not Size(10, 10).contains_point(Offset(-1, 0))
    assert not Size(10, 10).contains_point(Offset(0, -1))


def test_dimensions_contains_special():
    with pytest.raises(TypeError):
        (1, 2, 3) in Size(10, 10)

    assert (5, 5) in Size(10, 10)
    assert (9, 9) in Size(10, 10)
    assert (0, 0) in Size(10, 10)
    assert (10, 9) not in Size(10, 10)
    assert (9, 10) not in Size(10, 10)
    assert (-1, 0) not in Size(10, 10)
    assert (0, -1) not in Size(10, 10)


def test_dimensions_bool():
    assert Size(1, 1)
    assert Size(3, 4)
    assert not Size(0, 1)
    assert not Size(1, 0)


def test_dimensions_area():
    assert Size(0, 0).area == 0
    assert Size(1, 0).area == 0
    assert Size(1, 1).area == 1
    assert Size(4, 5).area == 20


def test_clamp():
    assert clamp(5, 0, 10) == 5
    assert clamp(-1, 0, 10) == 0
    assert clamp(11, 0, 10) == 10
    assert clamp(0, 0, 10) == 0
    assert clamp(10, 0, 10) == 10
    assert clamp(5, 10, 0) == 5


def test_offset_bool():
    assert Offset(1, 0)
    assert Offset(0, 1)
    assert Offset(0, -1)
    assert not Offset(0, 0)


def test_offset_is_origin():
    assert Offset(0, 0).is_origin
    assert not Offset(1, 0).is_origin


def test_clamped():
    assert Offset(-10, 0).clamped == Offset(0, 0)
    assert Offset(-10, -5).clamped == Offset(0, 0)
    assert Offset(5, -5).clamped == Offset(5, 0)
    assert Offset(5, 10).clamped == Offset(5, 10)


def test_offset_add():
    assert Offset(1, 1) + Offset(2, 2) == Offset(3, 3)
    assert Offset(1, 2) + Offset(3, 4) == Offset(4, 6)
    with pytest.raises(TypeError):
        Offset(1, 1) + "foo"


def test_offset_sub():
    assert Offset(1, 1) - Offset(2, 2) == Offset(-1, -1)
    assert Offset(3, 4) - Offset(2, 1) == Offset(1, 3)
    with pytest.raises(TypeError):
        Offset(1, 1) - "foo"


def test_offset_neg():
    assert Offset(0, 0) == Offset(0, 0)
    assert -Offset(2, -3) == Offset(-2, 3)


def test_offset_mul():
    assert Offset(2, 1) * 2 == Offset(4, 2)
    assert Offset(2, 1) * -2 == Offset(-4, -2)
    assert Offset(2, 1) * 0 == Offset(0, 0)
    with pytest.raises(TypeError):
        Offset(10, 20) * "foo"


def test_offset_blend():
    assert Offset(1, 2).blend(Offset(3, 4), 0) == Offset(1, 2)
    assert Offset(1, 2).blend(Offset(3, 4), 1) == Offset(3, 4)
    assert Offset(1, 2).blend(Offset(3, 4), 0.5) == Offset(2, 3)


def test_offset_get_distance_to():
    assert Offset(20, 30).get_distance_to(Offset(20, 30)) == 0
    assert Offset(0, 0).get_distance_to(Offset(1, 0)) == 1.0
    assert Offset(2, 1).get_distance_to(Offset(5, 5)) == 5.0


def test_region_null():
    assert Region() == Region(0, 0, 0, 0)
    assert not Region()


def test_region_from_union():
    with pytest.raises(ValueError):
        Region.from_union([])
    regions = [
        Region(10, 20, 30, 40),
        Region(15, 25, 5, 5),
        Region(30, 25, 20, 10),
    ]
    assert Region.from_union(regions) == Region(10, 20, 40, 40)


def test_region_from_offset():
    assert Region.from_offset(Offset(3, 4), (5, 6)) == Region(3, 4, 5, 6)


@pytest.mark.parametrize(
    "window,region,scroll",
    [
        (Region(0, 0, 200, 100), Region(0, 0, 200, 100), Offset(0, 0)),
        (Region(0, 0, 200, 100), Region(0, -100, 10, 10), Offset(0, -100)),
        (Region(10, 15, 20, 10), Region(0, 0, 50, 50), Offset(-10, -15)),
    ],
)
def test_get_scroll_to_visible(window, region, scroll):
    assert Region.get_scroll_to_visible(window, region) == scroll
    assert region.overlaps(window + scroll)


def test_region_area():
    assert Region(3, 4, 0, 0).area == 0
    assert Region(3, 4, 5, 6).area == 30


def test_region_size():
    assert isinstance(Region(3, 4, 5, 6).size, Size)
    assert Region(3, 4, 5, 6).size == Size(5, 6)


def test_region_origin():
    assert Region(1, 2, 3, 4).offset == Offset(1, 2)


def test_region_bottom_left():
    assert Region(1, 2, 3, 4).bottom_left == Offset(1, 6)


def test_region_top_right():
    assert Region(1, 2, 3, 4).top_right == Offset(4, 2)


def test_region_bottom_right():
    assert Region(1, 2, 3, 4).bottom_right == Offset(4, 6)


def test_region_add():
    assert Region(1, 2, 3, 4) + (10, 20) == Region(11, 22, 3, 4)
    with pytest.raises(TypeError):
        Region(1, 2, 3, 4) + "foo"


def test_region_sub():
    assert Region(11, 22, 3, 4) - (10, 20) == Region(1, 2, 3, 4)
    with pytest.raises(TypeError):
        Region(1, 2, 3, 4) - "foo"


def test_region_at_offset():
    assert Region(10, 10, 30, 40).at_offset((0, 0)) == Region(0, 0, 30, 40)
    assert Region(10, 10, 30, 40).at_offset((-15, 30)) == Region(-15, 30, 30, 40)


def test_crop_size():
    assert Region(10, 20, 100, 200).crop_size((50, 40)) == Region(10, 20, 50, 40)
    assert Region(10, 20, 100, 200).crop_size((500, 40)) == Region(10, 20, 100, 40)


def test_clip_size():
    assert Region(10, 10, 100, 80).clip_size((50, 100)) == Region(10, 10, 50, 80)


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
    assert Region(1, 2, 3, 4).translate((10, 20)) == Region(11, 22, 3, 4)
    assert Region(1, 2, 3, 4).translate((0, 20)) == Region(1, 22, 3, 4)


def test_region_contains_special():
    assert (10, 10) in Region(10, 10, 20, 30)
    assert (9, 10) not in Region(10, 10, 20, 30)
    assert Region(10, 10, 5, 5) in Region(10, 10, 20, 30)
    assert Region(5, 5, 5, 5) not in Region(10, 10, 20, 30)
    assert "foo" not in Region(0, 0, 10, 10)


def test_clip():
    assert Region(10, 10, 20, 30).clip(20, 25) == Region(10, 10, 10, 15)


def test_region_shrink():
    margin = Spacing(top=1, right=2, bottom=3, left=4)
    region = Region(x=10, y=10, width=50, height=50)
    assert region.shrink(margin) == Region(x=14, y=11, width=44, height=46)


def test_region_grow():
    margin = Spacing(top=1, right=2, bottom=3, left=4)
    region = Region(x=10, y=10, width=50, height=50)
    assert region.grow(margin) == Region(x=6, y=9, width=56, height=54)


def test_region_intersection():
    assert Region(0, 0, 100, 50).intersection(Region(10, 10, 10, 10)) == Region(
        10, 10, 10, 10
    )
    assert Region(10, 10, 30, 20).intersection(Region(20, 15, 60, 40)) == Region(
        20, 15, 20, 15
    )

    assert not Region(10, 10, 20, 30).intersection(Region(50, 50, 100, 200))


def test_region_union():
    assert Region(5, 5, 10, 10).union(Region(20, 30, 10, 5)) == Region(5, 5, 25, 30)


def test_size_add():
    assert Size(5, 10) + Size(2, 3) == Size(7, 13)
    with pytest.raises(TypeError):
        Size(1, 2) + "foo"


def test_size_sub():
    assert Size(5, 10) - Size(2, 3) == Size(3, 7)
    with pytest.raises(TypeError):
        Size(1, 2) - "foo"


def test_size_line_range():
    assert Size(20, 0).line_range == range(0)
    assert Size(0, 20).line_range == range(20)


def test_region_x_extents():
    assert Region(5, 10, 20, 30).column_span == (5, 25)


def test_region_y_extents():
    assert Region(5, 10, 20, 30).line_span == (10, 40)


def test_region_x_max():
    assert Region(5, 10, 20, 30).right == 25


def test_region_y_max():
    assert Region(5, 10, 20, 30).bottom == 40


def test_region_columns_range():
    assert Region(5, 10, 20, 30).column_range == range(5, 25)


def test_region_lines_range():
    assert Region(5, 10, 20, 30).line_range == range(10, 40)


def test_region_reset_offset():
    assert Region(5, 10, 20, 30).reset_offset == Region(0, 0, 20, 30)


def test_region_expand():
    assert Region(50, 10, 10, 5).expand((2, 3)) == Region(48, 7, 14, 11)


def test_spacing_bool():
    assert Spacing(1, 0, 0, 0)
    assert Spacing(0, 1, 0, 0)
    assert Spacing(0, 1, 0, 0)
    assert Spacing(0, 0, 1, 0)
    assert Spacing(0, 0, 0, 1)
    assert not Spacing(0, 0, 0, 0)


def test_spacing_width():
    assert Spacing(2, 3, 4, 5).width == 8


def test_spacing_height():
    assert Spacing(2, 3, 4, 5).height == 6


def test_spacing_top_left():
    assert Spacing(2, 3, 4, 5).top_left == (5, 2)


def test_spacing_bottom_right():
    assert Spacing(2, 3, 4, 5).bottom_right == (3, 4)


def test_spacing_totals():
    assert Spacing(2, 3, 4, 5).totals == (8, 6)


def test_spacing_css():
    assert Spacing(1, 1, 1, 1).css == "1"
    assert Spacing(1, 2, 1, 2).css == "1 2"
    assert Spacing(1, 2, 3, 4).css == "1 2 3 4"


def test_spacing_unpack():
    assert Spacing.unpack(1) == Spacing(1, 1, 1, 1)
    assert Spacing.unpack((1,)) == Spacing(1, 1, 1, 1)
    assert Spacing.unpack((1, 2)) == Spacing(1, 2, 1, 2)
    assert Spacing.unpack((1, 2, 3, 4)) == Spacing(1, 2, 3, 4)

    with pytest.raises(ValueError):
        assert Spacing.unpack(()) == Spacing(1, 2, 1, 2)

    with pytest.raises(ValueError):
        assert Spacing.unpack((1, 2, 3)) == Spacing(1, 2, 1, 2)

    with pytest.raises(ValueError):
        assert Spacing.unpack((1, 2, 3, 4, 5)) == Spacing(1, 2, 1, 2)


def test_spacing_add():
    assert Spacing(1, 2, 3, 4) + Spacing(5, 6, 7, 8) == Spacing(6, 8, 10, 12)

    with pytest.raises(TypeError):
        Spacing(1, 2, 3, 4) + "foo"


def test_spacing_sub():
    assert Spacing(1, 2, 3, 4) - Spacing(5, 6, 7, 8) == Spacing(-4, -4, -4, -4)

    with pytest.raises(TypeError):
        Spacing(1, 2, 3, 4) - "foo"


def test_spacing_convenience_constructors():
    assert Spacing.vertical(2) == Spacing(2, 0, 2, 0)
    assert Spacing.horizontal(2) == Spacing(0, 2, 0, 2)
    assert Spacing.all(2) == Spacing(2, 2, 2, 2)


def test_split():
    assert Region(10, 5, 22, 15).split(10, 5) == (
        Region(10, 5, 10, 5),
        Region(20, 5, 12, 5),
        Region(10, 10, 10, 10),
        Region(20, 10, 12, 10),
    )


def test_split_negative():
    assert Region(10, 5, 22, 15).split(-1, -1) == (
        Region(10, 5, 21, 14),
        Region(31, 5, 1, 14),
        Region(10, 19, 21, 1),
        Region(31, 19, 1, 1),
    )


def test_split_vertical():
    assert Region(10, 5, 22, 15).split_vertical(10) == (
        Region(10, 5, 10, 15),
        Region(20, 5, 12, 15),
    )


def test_split_vertical_negative():
    assert Region(10, 5, 22, 15).split_vertical(-1) == (
        Region(10, 5, 21, 15),
        Region(31, 5, 1, 15),
    )


def test_split_horizontal():
    assert Region(10, 5, 22, 15).split_horizontal(5) == (
        Region(10, 5, 22, 5),
        Region(10, 10, 22, 10),
    )


def test_split_horizontal_negative():
    assert Region(10, 5, 22, 15).split_horizontal(-1) == (
        Region(10, 5, 22, 14),
        Region(10, 19, 22, 1),
    )
