from rich.text import Span

from textual._fuzzy import Matcher


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
    print(spans)
    assert spans == [
        Span(0, 1, "bold"),
        Span(1, 2, "bold"),
        Span(2, 3, "bold"),
        Span(7, 8, "bold"),
        Span(8, 9, "bold"),
        Span(9, 10, "bold"),
        Span(10, 11, "bold"),
    ]
