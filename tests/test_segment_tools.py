from rich.segment import Segment
from rich.style import Style


from textual._segment_tools import line_crop


def test_line_crop():
    bold = Style(bold=True)
    italic = Style(italic=True)
    segments = [
        Segment("Hello", bold),
        Segment(" World!", italic),
    ]

    assert line_crop(segments, 1, 2) == [Segment("e", bold)]
    assert line_crop(segments, 4, 20) == [
        Segment("o", bold),
        Segment(" World!", italic),
    ]


def test_line_crop_emoji():
    bold = Style(bold=True)
    italic = Style(italic=True)
    segments = [
        Segment("Hello", bold),
        Segment("💩💩💩", italic),
    ]
    assert line_crop(segments, 8, 11) == [Segment(" 💩", italic)]
    assert line_crop(segments, 9, 11) == [Segment("💩", italic)]


def test_line_crop_edge():
    segments = [Segment("foo"), Segment("bar"), Segment("baz")]
    assert line_crop(segments, 2, 9) == [Segment("o"), Segment("bar"), Segment("baz")]
    assert line_crop(segments, 3, 9) == [Segment("bar"), Segment("baz")]
    assert line_crop(segments, 4, 9) == [Segment("ar"), Segment("baz")]
    assert line_crop(segments, 4, 8) == [Segment("ar"), Segment("ba")]


def test_line_crop_edge_2():
    segments = [
        Segment("╭─"),
        Segment(
            "────── Placeholder ───────",
        ),
        Segment(
            "─╮",
        ),
    ]
    result = line_crop(segments, 30, 60)
    expected = []
    print(repr(result))
    assert result == expected
