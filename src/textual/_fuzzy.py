from __future__ import annotations

from re import compile, escape

import rich.repr
from rich.style import Style
from rich.text import Text

from ._cache import LRUCache


@rich.repr.auto
class Matcher:
    """A fuzzy matcher."""

    def __init__(self, query: str, *, match_style: Style | None = None) -> None:
        """
        Args:
            query: A query as typed in by the user.
            match_style: The style to use to highlight matched portions of a string.
        """
        self._query = query
        self._match_style = Style(reverse=True) if match_style is None else match_style
        self._query_regex = ".*?".join(f"({escape(character)})" for character in query)
        self._query_regex_compiled = compile(self._query_regex)
        self._cache: LRUCache[str, float] = LRUCache(1024 * 4)

    @property
    def query(self) -> str:
        """The query string to look for."""
        return self._query

    def match(self, candidate: str) -> float:
        """Match the candidate against the query

        Args:
            candidate: Candidate string to match against.

        Returns:
            Strength of the match from 0 to 1.
        """
        cached = self._cache.get(candidate)
        if cached is not None:
            return cached
        match = self._query_regex_compiled.search(candidate)
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
            candidate: User candidate.

        Returns:
            A Text object with matched letters in bold.
        """
        match = self._query_regex_compiled.search(candidate)
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
    from rich import print

    matcher = Matcher("foo.bar")
    print(matcher.match("xz foo.bar sdf"))
    print(matcher.highlight("xz foo.bar sdf"))
