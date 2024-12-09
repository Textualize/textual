"""
Fuzzy matcher.

This class is used by the [command palette](/guide/command_palette) to match search terms.

"""

from __future__ import annotations

from dataclasses import dataclass, field
from re import IGNORECASE, compile, escape, finditer
from typing import Iterable

import rich.repr
from rich.style import Style
from rich.text import Text

from textual.cache import LRUCache


@dataclass
class FuzzyMatch:
    candidate_offset: int = 0
    query_offset: int = 0
    offsets: list[int] = field(default_factory=list)

    def advance(self, new_offset: int) -> FuzzyMatch:
        return FuzzyMatch(new_offset, self.query_offset, self.offsets.copy())


def match(
    query: str, candidate: str, case_sensitive: bool = False
) -> Iterable[list[int]]:
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

    stack: list[FuzzyMatch] = [FuzzyMatch(0, 0, [])]

    while stack:
        match = stack[-1]

        if match.candidate_offset >= len(candidate) or match.query_offset >= len(query):
            stack.pop()
            continue

        try:
            offset = candidate.index(query[match.query_offset], match.candidate_offset)
        except ValueError:
            # Current math was unsuccessful
            stack.pop()
            continue

        advance_match = match.advance(offset + 1)
        match.offsets.append(offset)
        match.candidate_offset = offset + 1
        match.query_offset += 1

        if match.query_offset == len(query):
            # Full match
            yield match.offsets.copy()
            stack.pop()

        stack.append(advance_match)

        # else:
        #     match.candidate_offset += 1
        #     stack.append(match_copy)

        # if query[match.query_offset] == candidate[match.candidate_offset]:
        #     match_copy = match.copy()
        #     match_copy.query_offset += 1
        #     if match_copy.query_offset == len(query):
        #         yield match_copy.offsets.copy()
        #     match_copy.offsets.append(match.candidate_offset)
        #     stack.append(match_copy)


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

    for offsets in match("ee", TEST):
        text = Text(TEST)
        for offset in offsets:
            text.stylize("reverse", offset, offset + 1)
        print(text)
