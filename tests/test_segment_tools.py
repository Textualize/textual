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
    total = sum(segment.cell_length for segment in segments)

    assert line_crop(segments, 1, 2, total) == [Segment("e", bold)]
    assert line_crop(segments, 4, 20, total) == [
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
    total = sum(segment.cell_length for segment in segments)
    assert line_crop(segments, 8, 11, total) == [Segment(" 💩", italic)]
    assert line_crop(segments, 9, 11, total) == [Segment("💩", italic)]


def test_line_crop_edge():
    segments = [Segment("foo"), Segment("bar"), Segment("baz")]
    total = sum(segment.cell_length for segment in segments)

    assert line_crop(segments, 2, 9, total) == [
        Segment("o"),
        Segment("bar"),
        Segment("baz"),
    ]
    assert line_crop(segments, 3, 9, total) == [Segment("bar"), Segment("baz")]
    assert line_crop(segments, 4, 9, total) == [Segment("ar"), Segment("baz")]
    assert line_crop(segments, 4, 8, total) == [Segment("ar"), Segment("ba")]


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
    total = sum(segment.cell_length for segment in segments)
    result = line_crop(segments, 30, 60, total)
    expected = []
    print(repr(result))
    assert result == expected
