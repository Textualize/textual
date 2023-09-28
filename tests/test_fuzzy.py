from rich.style import Style
from rich.text import Span

from textual.fuzzy import Matcher


def test_match():
    matcher = Matcher("foo.bar")

    # No match
    assert matcher.match("egg") == 0
    assert matcher.match("") == 0

    # Perfect match
    assert matcher.match("foo.bar") == 1.0
    # Perfect match (with superfluous characters)
    assert matcher.match("foo.bar sdf") == 1.0
    assert matcher.match("xz foo.bar sdf") == 1.0

    # Partial matches
    # 2 Groups
    assert matcher.match("foo egg.bar") == 1.0 - 1 / 11

    # 3 Groups
    assert matcher.match("foo .ba egg r") == 1.0 - 2 / 13


def test_highlight():
    matcher = Matcher("foo.bar")

    spans = matcher.highlight("foo/egg.bar").spans
    assert spans == [
        Span(0, 1, Style(reverse=True)),
        Span(1, 2, Style(reverse=True)),
        Span(2, 3, Style(reverse=True)),
        Span(7, 8, Style(reverse=True)),
        Span(8, 9, Style(reverse=True)),
        Span(9, 10, Style(reverse=True)),
        Span(10, 11, Style(reverse=True)),
    ]
