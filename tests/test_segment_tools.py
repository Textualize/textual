from rich.segment import Segment
from rich.style import Style

from textual._segment_tools import align_lines, line_crop, line_pad, line_trim
from textual.geometry import Size


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


def test_line_trim_ascii():
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


def test_align_lines_vertical_middle():
    """Regression test for an issue found while working on
    https://github.com/Textualize/textual/issues/3628 - an extra vertical line
    was being produced when aligning. If you passed in a Size of height=1 to
    `align_lines`, it was producing a result containing 2 lines instead of 1."""
    lines = [[Segment("  "), Segment("hello"), Segment("   ")]]
    result = align_lines(
        lines, Style(), size=Size(10, 3), horizontal="center", vertical="middle"
    )
    assert list(result) == [
        [Segment("          ", Style())],
        [Segment("  "), Segment("hello"), Segment("   ")],
        [Segment("          ", Style())],
    ]


def test_align_lines_top_left():
    lines = [
        [Segment("hello")],
        [Segment("world")],
    ]

    result = align_lines(
        lines, Style(), size=Size(10, 4), horizontal="left", vertical="top"
    )

    assert list(result) == [
        [Segment("hello"), Segment("     ", Style())],
        [Segment("world"), Segment("     ", Style())],
        [Segment("          ", Style())],
        [Segment("          ", Style())],
    ]


def test_align_lines_top_right():
    lines = [
        [Segment("hello")],
        [Segment("world")],
    ]

    result = align_lines(
        lines, Style(), size=Size(10, 4), horizontal="right", vertical="top"
    )

    assert list(result) == [
        [Segment("     ", Style()), Segment("hello")],
        [Segment("     ", Style()), Segment("world")],
        [Segment("          ", Style())],
        [Segment("          ", Style())],
    ]


def test_align_lines_perfect_fit_horizontal_left():
    lines = [[Segment("  "), Segment("hello"), Segment("   ")]]  # 10 cells
    result = align_lines(
        lines, Style(), size=Size(10, 1), horizontal="left", vertical="middle"
    )
    assert list(result) == [[Segment("  "), Segment("hello"), Segment("   ")]]


def test_align_lines_perfect_fit_horizontal_center():
    """When the content perfectly fits the available horizontal space,
    no empty segments should be produced. This is a regression test for
    the issue https://github.com/Textualize/textual/issues/3628."""
    lines = [[Segment("  "), Segment("hello"), Segment("   ")]]  # 10 cells of content
    result = align_lines(
        lines, Style(), size=Size(10, 1), horizontal="center", vertical="middle"
    )
    assert list(result) == [[Segment("  "), Segment("hello"), Segment("   ")]]


def test_align_lines_perfect_fit_horizontal_right():
    """When the content perfectly fits the available horizontal space,
    no empty segments should be produced. This is a regression test for
    the issue https://github.com/Textualize/textual/issues/3628."""
    lines = [[Segment("  "), Segment("hello"), Segment("   ")]]  # 10 cells of content
    result = align_lines(
        lines, Style(), size=Size(10, 1), horizontal="right", vertical="middle"
    )
    assert list(result) == [[Segment("  "), Segment("hello"), Segment("   ")]]
