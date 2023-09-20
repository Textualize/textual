"""
Fuzzy matcher.

This class is used by the [command palette](guide/command_palette) to match search terms.

"""

from __future__ import annotations

from re import IGNORECASE, compile, escape

import rich.repr
from rich.style import Style
from rich.text import Text

from ._cache import LRUCache


@rich.repr.auto
class Matcher:
    """A fuzzy matcher."""

    def __init__(
        self,
        query: str,
        *,
        match_style: Style | None = None,
        case_sensitive: bool = False,
    ) -> None:
        """Initialise the fuzzy matching object.

        Args:
            query: A query as typed in by the user.
            match_style: The style to use to highlight matched portions of a string.
            case_sensitive: Should matching be case sensitive?
        """
        self._query = query
        self._match_style = Style(reverse=True) if match_style is None else match_style
        self._query_regex = compile(
            ".*?".join(f"({escape(character)})" for character in query),
            flags=0 if case_sensitive else IGNORECASE,
        )
        self._cache: LRUCache[str, float] = LRUCache(1024 * 4)

    @property
    def query(self) -> str:
        """The query string to look for."""
        return self._query

    @property
    def match_style(self) -> Style:
        """The style that will be used to highlight hits in the matched text."""
        return self._match_style

    @property
    def query_pattern(self) -> str:
        """The regular expression pattern built from the query."""
        return self._query_regex.pattern

    @property
    def case_sensitive(self) -> bool:
        """Is this matcher case sensitive?"""
        return not bool(self._query_regex.flags & IGNORECASE)

    def match(self, candidate: str) -> float:
        """Match the candidate against the query.

        Args:
            candidate: Candidate string to match against the query.

        Returns:
            Strength of the match from 0 to 1.
        """
        cached = self._cache.get(candidate)
        if cached is not None:
            return cached
        match = self._query_regex.search(candidate)
        if match is None:
            score = 0.0
        else:
            assert match.lastindex is not None
            offsets = [
                match.span(group_no)[0] for group_no in range(1, match.lastindex + 1)
            ]
            group_count = 0
            last_offset = -2
            for offset in offsets:
                if offset > last_offset + 1:
                    group_count += 1
                last_offset = offset

            score = 1.0 - ((group_count - 1) / len(candidate))
        self._cache[candidate] = score
        return score

    def highlight(self, candidate: str) -> Text:
        """Highlight the candidate with the fuzzy match.

        Args:
            candidate: The candidate string to match against the query.

        Returns:
            A [rich.text.Text][`Text`] object with highlighted matches.
        """
        match = self._query_regex.search(candidate)
        text = Text(candidate)
        if match is None:
            return text
        assert match.lastindex is not None
        offsets = [
            match.span(group_no)[0] for group_no in range(1, match.lastindex + 1)
        ]
        for offset in offsets:
            text.stylize(self._match_style, offset, offset + 1)

        return text


if __name__ == "__main__":
    from itertools import permutations
    from string import ascii_lowercase
    from time import monotonic

    from rich import print
    from rich.rule import Rule

    matcher = Matcher("foo.bar")
    print(Rule())
    print("Query is:", matcher.query)
    print("Rule is:", matcher.query_pattern)
    print(Rule())
    candidates = (
        "foo.bar",
        " foo.bar ",
        "Hello foo.bar world",
        "f o o . b a r",
        "f o o .bar",
        "foo. b a r",
        "Lots of text before the foo.bar",
        "foo.bar up front and then lots of text afterwards",
        "This has an o in it but does not have a match",
        "Let's find one obvious match. But blat around always roughly.",
    )
    results = sorted(
        [
            (matcher.match(candidate), matcher.highlight(candidate))
            for candidate in candidates
        ],
        key=lambda pair: pair[0],
        reverse=True,
    )
    for score, highlight in results:
        print(f"{score:.15f} '", highlight, "'", sep="")
    print(Rule())

    RUNS = 5
    candidates = [
        "".join(permutation) for permutation in permutations(ascii_lowercase[:10])
    ]
    matcher = Matcher(ascii_lowercase[:10])
    start = monotonic()
    for _ in range(RUNS):
        for candidate in candidates:
            _ = matcher.match(candidate)
    print(f"{RUNS * len(candidates)} matches in {monotonic() - start:.5f} seconds")
