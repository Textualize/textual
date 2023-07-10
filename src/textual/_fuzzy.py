from re import compile, escape

import rich.repr
from rich.text import Text

from ._cache import LRUCache


@rich.repr.auto
class Matcher:
    """A fuzzy matcher."""

    def __init__(self, query: str) -> None:
        """
        Args:
            query: A query as typed in by the user.
        """
        self.query = query
        self._query_regex = ".*?".join(f"({escape(character)})" for character in query)
        self._query_regex_compiled = compile(self._query_regex)
        self._cache: LRUCache[str, float] = LRUCache(1024 * 4)

    def match(self, input: str) -> float:
        """Match the input against the query

        Args:
            input: Input string to match against.

        Returns:
            Strength of the match from 0 to 1.
        """
        cached = self._cache.get(input)
        if cached is not None:
            return cached
        match = self._query_regex_compiled.search(input)
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

            score = 1.0 - ((group_count - 1) / len(input))
        self._cache[input] = score
        return score

    def highlight(self, input: str) -> Text:
        """Highlight the input with the fuzzy match.

        Args:
            input: User input.

        Returns:
            A Text object with matched letters in bold.
        """
        match = self._query_regex_compiled.search(input)
        text = Text(input)
        if match is None:
            return text
        assert match.lastindex is not None
        offsets = [
            match.span(group_no)[0] for group_no in range(1, match.lastindex + 1)
        ]
        for offset in offsets:
            text.stylize("bold", offset, offset + 1)

        return text


if __name__ == "__main__":
    from rich import print

    matcher = Matcher("foo.bar")
    print(matcher.match("xz foo.bar sdf"))
    print(matcher.highlight("xz foo.bar sdf"))
