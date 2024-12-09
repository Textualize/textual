"""
Fuzzy matcher.

This class is used by the [command palette](/guide/command_palette) to match search terms.

"""

from __future__ import annotations

from re import IGNORECASE, compile, escape, finditer
from typing import Iterable, NamedTuple

import rich.repr
from rich.style import Style
from rich.text import Text

from textual.cache import LRUCache


class Search(NamedTuple):
    candidate_offset: int = 0
    query_offset: int = 0
    offsets: tuple[int, ...] = ()

    def branch(self, offset: int) -> tuple[Search, Search]:
        return (
            Search(offset + 1, self.query_offset + 1, self.offsets + (offset,)),
            Search(offset + 1, self.query_offset, self.offsets),
        )


def match(
    query: str, candidate: str, case_sensitive: bool = False
) -> Iterable[tuple[int, ...]]:
    if not case_sensitive:
        query = query.lower()
        candidate = candidate.lower()

    query_letters: list[tuple[float, int, str]] = []
    for word_match in finditer(r"\w+", candidate):
        start, end = word_match.span()

        query_letters.extend(
            [
                (True, start, candidate[start]),
                *[
                    (False, offset, candidate[offset])
                    for offset in range(start + 1, end)
                ],
            ]
        )

    stack: list[Search] = [Search()]
    push = stack.append
    pop = stack.pop
    query_size = len(query)

    while stack:
        search = stack[-1]
        offset = candidate.find(
            query[search.query_offset],
            search.candidate_offset,
        )
        if offset == -1:
            pop()
        else:
            advance_branch, stack[-1] = search.branch(offset)
            if advance_branch.query_offset == query_size:
                yield advance_branch.offsets
            else:
                push(advance_branch)


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
        self._case_sensitive = case_sensitive
        self._query_regex = compile(
            ".*?".join(f"({escape(character)})" for character in query),
            flags=0 if case_sensitive else IGNORECASE,
        )
        _first_word_regex = ".*?".join(
            f"(\\b{escape(character)})" for character in query
        )
        self._first_word_regex = compile(
            _first_word_regex,
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
        return self._case_sensitive

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
            multiplier = 1.0
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

            if first_words := self._first_word_regex.search(candidate):
                multiplier = len(first_words.groups()) + 1
                # boost if the query matches first words

            score *= multiplier
        self._cache[candidate] = score
        return score

    def highlight(self, candidate: str) -> Text:
        """Highlight the candidate with the fuzzy match.

        Args:
            candidate: The candidate string to match against the query.

        Returns:
            A [rich.text.Text][`Text`] object with highlighted matches.
        """
        text = Text.from_markup(candidate)
        match = self._first_word_regex.search(candidate)
        if match is None:
            match = self._query_regex.search(candidate)

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
    TEST = "Save Screenshot"
    from rich import print
    from rich.text import Text

    for offsets in match("shot", TEST):
        text = Text(TEST)
        for offset in offsets:
            text.stylize("reverse", offset, offset + 1)
        print(text)
