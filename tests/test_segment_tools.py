from rich.segment import Segment
from rich.style import Style

from textual._segment_tools import line_crop, line_trim, line_pad


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


def test_line_crop_highlight_reverse_bug():
    """Regression test for #818"""
    segments_joined = [Segment('a1あ１１bcdaef１２３a1a')]
    segments_split = [Segment('a1あ１１bcdaef'), Segment('１'), Segment('２３a1a')]

    joined1 = "".join(seg.text for seg in line_crop(segments_split, start=9, end=16, total=23))
    joined2 = "".join(seg.text for seg in line_crop(segments_joined, start=9, end=16, total=23))

    assert joined1 == joined2


def test_line_trim():
    segments = [Segment("foo")]

    assert line_trim(segments, False, False) == segments
    assert line_trim(segments, True, False) == [Segment("oo")]
    assert line_trim(segments, False, True) == [Segment("fo")]
    assert line_trim(segments, True, True) == [Segment("o")]

    fob_segments = [Segment("f"), Segment("o"), Segment("b")]

    assert line_trim(fob_segments, True, False) == [
        Segment("o"),
        Segment("b"),
    ]

    assert line_trim(fob_segments, False, True) == [
        Segment("f"),
        Segment("o"),
    ]

    assert line_trim(fob_segments, True, True) == [
        Segment("o"),
    ]

    assert line_trim([], True, True) == []


def test_line_pad():
    segments = [Segment("foo"), Segment("bar")]
    style = Style.parse("red")
    assert line_pad(segments, 2, 3, style) == [
        Segment("  ", style),
        *segments,
        Segment("   ", style),
    ]

    assert line_pad(segments, 0, 3, style) == [
        *segments,
        Segment("   ", style),
    ]

    assert line_pad(segments, 2, 0, style) == [
        Segment("  ", style),
        *segments,
    ]

    assert line_pad(segments, 0, 0, style) == segments
