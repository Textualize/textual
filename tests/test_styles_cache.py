from __future__ import annotations

from rich.segment import Segment
from rich.style import Style

from textual._styles_cache import StylesCache
from textual.color import Color
from textual.css.styles import Styles
from textual.geometry import Region, Size
from textual.strip import Strip


def _extract_content(lines: list[Strip]) -> list[str]:
    """Extract the text content from lines."""
    content = ["".join(segment.text for segment in line) for line in lines]
    return content


def test_set_dirty():
    cache = StylesCache()
    cache.set_dirty(Region(3, 4, 10, 2))
    assert not cache.is_dirty(3)
    assert cache.is_dirty(4)
    assert cache.is_dirty(5)
    assert not cache.is_dirty(6)


def test_no_styles():
    """Test that empty style returns the content un-altered"""
    content = [
        Strip([Segment("foo")]),
        Strip([Segment("bar")]),
        Strip([Segment("baz")]),
    ]
    styles = Styles()
    cache = StylesCache()
    lines = cache.render(
        styles,
        Size(3, 3),
        Color.parse("blue"),
        Color.parse("green"),
        content.__getitem__,
        content_size=Size(3, 3),
    )
    style = Style.from_color(bgcolor=Color.parse("green").rich_color)
    expected = [
        Strip([Segment("foo", style)], 3),
        Strip([Segment("bar", style)], 3),
        Strip([Segment("baz", style)], 3),
    ]

    assert lines == expected


def test_border():
    content = [
        Strip([Segment("foo")]),
        Strip([Segment("bar")]),
        Strip([Segment("baz")]),
    ]
    styles = Styles()
    styles.border = ("heavy", "white")
    cache = StylesCache()
    lines = cache.render(
        styles,
        Size(5, 5),
        Color.parse("blue"),
        Color.parse("green"),
        content.__getitem__,
        content_size=Size(3, 3),
    )

    text_content = _extract_content(lines)

    expected_text = [
        "┏━━━┓",
        "┃foo┃",
        "┃bar┃",
        "┃baz┃",
        "┗━━━┛",
    ]

    assert text_content == expected_text


def test_padding():
    content = [
        Strip([Segment("foo")]),
        Strip([Segment("bar")]),
        Strip([Segment("baz")]),
    ]
    styles = Styles()
    styles.padding = 1
    cache = StylesCache()
    lines = cache.render(
        styles,
        Size(5, 5),
        Color.parse("blue"),
        Color.parse("green"),
        content.__getitem__,
        content_size=Size(3, 3),
    )

    text_content = _extract_content(lines)

    expected_text = [
        "     ",
        " foo ",
        " bar ",
        " baz ",
        "     ",
    ]

    assert text_content == expected_text


def test_padding_border():
    content = [
        Strip([Segment("foo")]),
        Strip([Segment("bar")]),
        Strip([Segment("baz")]),
    ]
    styles = Styles()
    styles.padding = 1
    styles.border = ("heavy", "white")
    cache = StylesCache()
    lines = cache.render(
        styles,
        Size(7, 7),
        Color.parse("blue"),
        Color.parse("green"),
        content.__getitem__,
        content_size=Size(3, 3),
    )

    text_content = _extract_content(lines)

    expected_text = [
        "┏━━━━━┓",
        "┃     ┃",
        "┃ foo ┃",
        "┃ bar ┃",
        "┃ baz ┃",
        "┃     ┃",
        "┗━━━━━┛",
    ]

    assert text_content == expected_text


def test_outline():
    content = [
        Strip([Segment("foo")]),
        Strip([Segment("bar")]),
        Strip([Segment("baz")]),
    ]
    styles = Styles()
    styles.outline = ("heavy", "white")
    cache = StylesCache()
    lines = cache.render(
        styles,
        Size(3, 3),
        Color.parse("blue"),
        Color.parse("green"),
        content.__getitem__,
        content_size=Size(3, 3),
    )

    text_content = _extract_content(lines)
    expected_text = [
        "┏━┓",
        "┃a┃",
        "┗━┛",
    ]
    assert text_content == expected_text


def test_crop():
    content = [
        Strip([Segment("foo")]),
        Strip([Segment("bar")]),
        Strip([Segment("baz")]),
    ]
    styles = Styles()
    styles.padding = 1
    styles.border = ("heavy", "white")
    cache = StylesCache()
    lines = cache.render(
        styles,
        Size(7, 7),
        Color.parse("blue"),
        Color.parse("green"),
        content.__getitem__,
        content_size=Size(3, 3),
        crop=Region(2, 2, 3, 3),
    )
    text_content = _extract_content(lines)
    expected_text = [
        "foo",
        "bar",
        "baz",
    ]
    assert text_content == expected_text


def test_dirty_cache() -> None:
    """Check that we only render content once or if it has been marked as dirty."""

    content = [
        Strip([Segment("foo")]),
        Strip([Segment("bar")]),
        Strip([Segment("baz")]),
    ]
    rendered_lines: list[int] = []

    def get_content_line(y: int) -> Strip:
        rendered_lines.append(y)
        return content[y]

    styles = Styles()
    styles.padding = 1
    styles.border = ("heavy", "white")
    cache = StylesCache()
    lines = cache.render(
        styles,
        Size(7, 7),
        Color.parse("blue"),
        Color.parse("green"),
        get_content_line,
        Size(3, 3),
    )
    assert rendered_lines == [0, 1, 2]
    del rendered_lines[:]

    text_content = _extract_content(lines)

    expected_text = [
        "┏━━━━━┓",
        "┃     ┃",
        "┃ foo ┃",
        "┃ bar ┃",
        "┃ baz ┃",
        "┃     ┃",
        "┗━━━━━┛",
    ]
    assert text_content == expected_text

    # Re-render styles, check that content was not requested
    lines = cache.render(
        styles,
        Size(7, 7),
        Color.parse("blue"),
        Color.parse("green"),
        get_content_line,
        content_size=Size(3, 3),
    )
    assert rendered_lines == []
    del rendered_lines[:]
    text_content = _extract_content(lines)
    assert text_content == expected_text

    # Mark 2 lines as dirty
    cache.set_dirty(Region(0, 2, 7, 2))

    lines = cache.render(
        styles,
        Size(7, 7),
        Color.parse("blue"),
        Color.parse("green"),
        get_content_line,
        content_size=Size(3, 3),
    )
    assert rendered_lines == [0, 1]
    text_content = _extract_content(lines)
    assert text_content == expected_text
