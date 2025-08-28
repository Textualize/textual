"""
Fuzzy matcher.

This class is used by the [command palette](/guide/command_palette) to match search terms.

"""

from __future__ import annotations

from functools import lru_cache
from operator import itemgetter
from re import finditer
from typing import Iterable, Sequence

import rich.repr

from textual.cache import LRUCache
from textual.content import Content
from textual.visual import Style


class FuzzySearch:
    """Performs a fuzzy search.

    Unlike a regex solution, this will finds all possible matches.
    """

    def __init__(
        self, case_sensitive: bool = False, *, cache_size: int = 1024 * 4
    ) -> None:
        """Initialize fuzzy search.

        Args:
            case_sensitive: Is the match case sensitive?
            cache_size: Number of queries to cache.
        """

        self.case_sensitive = case_sensitive
        self.cache: LRUCache[tuple[str, str], tuple[float, Sequence[int]]] = LRUCache(
            cache_size
        )

    def match(self, query: str, candidate: str) -> tuple[float, Sequence[int]]:
        """Match against a query.

        Args:
            query: The fuzzy query.
            candidate: A candidate to check,.

        Returns:
            A pair of (score, tuple of offsets). `(0, ())` for no result.
        """

        cache_key = (query, candidate)
        if cache_key in self.cache:
            return self.cache[cache_key]
        default: tuple[float, Sequence[int]] = (0.0, [])
        result = max(self._match(query, candidate), key=itemgetter(0), default=default)
        self.cache[cache_key] = result
        return result

    @classmethod
    @lru_cache(maxsize=1024)
    def get_first_letters(cls, candidate: str) -> frozenset[int]:
        return frozenset({match.start() for match in finditer(r"\w+", candidate)})

    def score(self, candidate: str, positions: Sequence[int]) -> float:
        """Score a search.

        Args:
            search: Search object.

        Returns:
            Score.
        """
        first_letters = self.get_first_letters(candidate)
        # This is a heuristic, and can be tweaked for better results
        # Boost first letter matches
        offset_count = len(positions)
        score: float = offset_count + len(first_letters.intersection(positions))

        groups = 1
        last_offset, *offsets = positions
        for offset in offsets:
            if offset != last_offset + 1:
                groups += 1
            last_offset = offset

        # Boost to favor less groups
        normalized_groups = (offset_count - (groups - 1)) / offset_count
        score *= 1 + (normalized_groups * normalized_groups)
        return score

    def _match(
        self, query: str, candidate: str
    ) -> Iterable[tuple[float, Sequence[int]]]:
        letter_positions: list[list[int]] = []
        position = 0

        if not self.case_sensitive:
            candidate = candidate.lower()
            query = query.lower()
        score = self.score
        if query in candidate:
            # Quick exit when the query exists as a substring
            query_location = candidate.rfind(query)
            offsets = list(range(query_location, query_location + len(query)))
            yield (
                score(candidate, offsets) * (2.0 if candidate == query else 1.5),
                offsets,
            )
            return

        for offset, letter in enumerate(query):
            last_index = len(candidate) - offset
            positions: list[int] = []
            letter_positions.append(positions)
            index = position
            while (location := candidate.find(letter, index)) != -1:
                positions.append(location)
                index = location + 1
                if index >= last_index:
                    break
            if not positions:
                yield (0.0, ())
                return
            position = positions[0] + 1

        possible_offsets: list[list[int]] = []
        query_length = len(query)

        def get_offsets(offsets: list[int], positions_index: int) -> None:
            """Recursively match offsets.

            Args:
                offsets: A list of offsets.
                positions_index: Index of query letter.

            """
            for offset in letter_positions[positions_index]:
                if not offsets or offset > offsets[-1]:
                    new_offsets = [*offsets, offset]
                    if len(new_offsets) == query_length:
                        possible_offsets.append(new_offsets)
                    else:
                        get_offsets(new_offsets, positions_index + 1)

        get_offsets([], 0)

        for offsets in possible_offsets:
            yield score(candidate, offsets), offsets


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
        self.fuzzy_search = FuzzySearch()

    @property
    def query(self) -> str:
        """The query string to look for."""
        return self._query

    @property
    def match_style(self) -> Style:
        """The style that will be used to highlight hits in the matched text."""
        return self._match_style

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
        return self.fuzzy_search.match(self.query, candidate)[0]

    def highlight(self, candidate: str) -> Content:
        """Highlight the candidate with the fuzzy match.

        Args:
            candidate: The candidate string to match against the query.

        Returns:
            A [`Text`][rich.text.Text] object with highlighted matches.
        """
        content = Content.from_markup(candidate)
        score, offsets = self.fuzzy_search.match(self.query, candidate)
        if not score:
            return content
        for offset in offsets:
            if not candidate[offset].isspace():
                content = content.stylize(self._match_style, offset, offset + 1)
        return content


if __name__ == "__main__":
    fuzzy_search = FuzzySearch()
    fuzzy_search.match("foo.bar", "foo/egg.bar")
