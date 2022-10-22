from __future__ import annotations

from typing import Iterable


def friendly_list(
    words: Iterable[str], joiner: str = "or", omit_empty: bool = True
) -> str:
    """Generate a list of words as readable prose.

    >>> friendly_list(["foo", "bar", "baz"])
    "'foo', 'bar', or 'baz'"

    Args:
        words (Iterable[str]): A list of words.
        joiner (str, optional): The last joiner word. Defaults to "or".

    Returns:
        str: List as prose.
    """
    words = [
        repr(word) for word in sorted(words, key=str.lower) if word or not omit_empty
    ]
    if len(words) == 1:
        return words[0]
    elif len(words) == 2:
        word1, word2 = words
        return f"{word1} {joiner} {word2}"
    else:
        return f'{", ".join(words[:-1])}, {joiner} {words[-1]}'
