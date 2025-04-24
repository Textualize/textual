"""
Fuzzy matcher.

This class is used by the [command palette](/guide/command_palette) to match search terms.

"""

from __future__ import annotations

from operator import itemgetter
from re import IGNORECASE, escape, finditer, search
from typing import Iterable, NamedTuple

import rich.repr

from textual.cache import LRUCache
from textual.content import Content
from textual.visual import Style


class _Search(NamedTuple):
    """Internal structure to keep track of a recursive search."""

    candidate_offset: int = 0
    query_offset: int = 0
    offsets: tuple[int, ...] = ()

    def branch(self, offset: int) -> tuple[_Search, _Search]:
        """Branch this search when an offset is found.

        Args:
            offset: Offset of a matching letter in the query.

        Returns:
            A pair of search objects.
        """
        _, query_offset, offsets = self
        return (
            _Search(offset + 1, query_offset + 1, offsets + (offset,)),
            _Search(offset + 1, query_offset, offsets),
        )

    @property
    def groups(self) -> int:
        """Number of groups in offsets."""
        groups = 1
        last_offset, *offsets = self.offsets
        for offset in offsets:
            if offset != last_offset + 1:
                groups += 1
            last_offset = offset
        return groups


class FuzzySearch:
    """Performs a fuzzy search.

    Unlike a regex solution, this will finds all possible matches.
    """

    cache: LRUCache[tuple[str, str, bool], tuple[float, tuple[int, ...]]] = LRUCache(
        1024 * 4
    )

    def __init__(self, case_sensitive: bool = False) -> None:
        """Initialize fuzzy search.

        Args:
            case_sensitive: Is the match case sensitive?
        """

        self.case_sensitive = case_sensitive

    def match(self, query: str, candidate: str) -> tuple[float, tuple[int, ...]]:
        """Match against a query.

        Args:
            query: The fuzzy query.
            candidate: A candidate to check,.

        Returns:
            A pair of (score, tuple of offsets). `(0, ())` for no result.
        """
        query_regex = ".*?".join(f"({escape(character)})" for character in query)
        if not search(
            query_regex, candidate, flags=0 if self.case_sensitive else IGNORECASE
        ):
            # Bail out early if there is no possibility of a match
            return (0.0, ())

        cache_key = (query, candidate, self.case_sensitive)
        if cache_key in self.cache:
            return self.cache[cache_key]
        result = max(
            self._match(query, candidate), key=itemgetter(0), default=(0.0, ())
        )
        self.cache[cache_key] = result
        return result

    def _match(
        self, query: str, candidate: str
    ) -> Iterable[tuple[float, tuple[int, ...]]]:
        """Generator to do the matching.

        Args:
            query: Query to match.
            candidate: Candidate to check against.

        Yields:
            Pairs of score and tuple of offsets.
        """
        if not self.case_sensitive:
            query = query.lower()
            candidate = candidate.lower()

        # We need this to give a bonus to first letters.
        first_letters = {match.start() for match in finditer(r"\w+", candidate)}

        def score(search: _Search) -> float:
            """Sore a search.

            Args:
                search: Search object.

            Returns:
                Score.

            """
            # This is a heuristic, and can be tweaked for better results
            # Boost first letter matches
            offset_count = len(search.offsets)
            score: float = offset_count + len(
                first_letters.intersection(search.offsets)
            )
            # Boost to favor less groups
            normalized_groups = (offset_count - (search.groups - 1)) / offset_count
            score *= 1 + (normalized_groups * normalized_groups)
            return score

        stack: list[_Search] = [_Search()]
        push = stack.append
        pop = stack.pop
        query_size = len(query)
        find = candidate.find
        # Limit the number of loops out of an abundance of caution.
        # This should be hard to reach without contrived data.
        remaining_loops = 10_000
        while stack and (remaining_loops := remaining_loops - 1):
            search = pop()
            offset = find(query[search.query_offset], search.candidate_offset)
            if offset != -1:
                if not set(candidate[search.candidate_offset :]).issuperset(
                    query[search.query_offset :]
                ):
                    # Early out if there is not change of a match
                    continue
                advance_branch, branch = search.branch(offset)
                if advance_branch.query_offset == query_size:
                    yield score(advance_branch), advance_branch.offsets
                    push(branch)
                else:
                    push(branch)
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
