from textual.content import Span
from textual.fuzzy import Matcher
from textual.style import Style


def test_no_match():
    """Check non matching score of zero."""
    matcher = Matcher("x")
    assert matcher.match("foo") == 0


def test_match_single_group():
    """Check that single groups rang higher."""
    matcher = Matcher("abc")
    assert matcher.match("foo abc bar") > matcher.match("fooa barc")


def test_boosted_matches():
    """Check first word matchers rank higher."""
    matcher = Matcher("ss")

    # First word matchers should score higher
    assert matcher.match("Save Screenshot") > matcher.match("Show Keys abcde")


def test_highlight():
    matcher = Matcher("foo.bar")

    spans = matcher.highlight("foo/egg.bar").spans
    print(repr(spans))
    assert spans == [
        Span(0, 1, Style(reverse=True)),
        Span(1, 2, Style(reverse=True)),
        Span(2, 3, Style(reverse=True)),
        Span(7, 8, Style(reverse=True)),
        Span(8, 9, Style(reverse=True)),
        Span(9, 10, Style(reverse=True)),
        Span(10, 11, Style(reverse=True)),
    ]


def test_whole_word_boost():
    """Whole word matches should score higher than word-start matches."""
    matcher = Matcher("cmd")
    # Exact match (4.0x) should be highest
    exact_score = matcher.match("cmd")
    # Whole-word in multi-word string (3.5x) should be second
    whole_word_score = matcher.match("cmd palette")
    # Word-start (2.5x) should be third
    word_start_score = matcher.match("cmd123")
    # Regular substring (1.5x) should be fourth
    substring_score = matcher.match("mycmd")
    # Fuzzy match (1.0x) should be lowest
    fuzzy_score = matcher.match("command")

    assert exact_score > whole_word_score, "Exact match should beat whole-word in multi-word"
    assert whole_word_score > word_start_score, "Whole-word should beat word-start"
    assert word_start_score > substring_score, "Word-start should beat substring"
    assert substring_score > fuzzy_score, "Substring should beat fuzzy"


def test_word_start_vs_substring():
    """Word-start matches should score higher than regular substring matches."""
    matcher = Matcher("test")
    # Word-start match (test in "test file")
    word_start_score = matcher.match("test file")
    # Substring match (test in "mytest")
    substring_score = matcher.match("mytest")

    assert word_start_score > substring_score


def test_whole_word_with_numbers():
    """Word boundaries should work with alphanumeric boundaries."""
    matcher = Matcher("cmd")
    # "cmd123" is a word-start match (cmd at start of "word")
    assert matcher.match("cmd123") > matcher.match("mycmd")
    # "123cmd" is NOT a word-start match (cmd not at word boundary)
    assert matcher.match("cmd123") > matcher.match("123cmd")


def test_case_sensitive_word_boundaries():
    """Word boundary boosts should respect case_sensitive setting."""
    matcher_cs = Matcher("Test", case_sensitive=True)
    matcher_ci = Matcher("Test", case_sensitive=False)
    # Case-sensitive: "Test" in "Test file" should boost
    assert matcher_cs.match("Test file") > matcher_cs.match("test file")
    # Case-insensitive: both should boost equally
    assert matcher_ci.match("Test file") == matcher_ci.match("test file")


def test_multi_word_query():
    """Multi-word queries should get word boundary boosts."""
    matcher = Matcher("save screen")
    # Whole word match (save screen in "save screen") - highest
    whole_word = matcher.match("save screen")
    # Word-start match (save screen in "save screenshot") - medium
    word_start = matcher.match("save screenshot")
    # Regular match (save screen in "save my screen") - lower
    regular = matcher.match("save my screen")

    assert whole_word > word_start > regular


def test_no_word_boundary_match():
    """Queries without word boundaries should use normal fuzzy matching."""
    matcher = Matcher("abc")
    # "abc" should get whole-word boost
    abc_score = matcher.match("abc")
    # "a-b-c" has no word boundaries, should use fuzzy scoring
    fuzzy_score = matcher.match("a-b-c")
    # abc should score much higher due to whole-word boost
    assert abc_score > fuzzy_score * 2
