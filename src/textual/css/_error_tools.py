from __future__ import annotations

from typing import Iterable


def friendly_list(words: Iterable[str], joiner: str = "or") -> str:

    words = [repr(word) for word in sorted(words, key=str.lower)]
    if len(words) == 1:
        return words[0]
    else:
        return f'{", ".join(words[:-1])} {joiner} {words[-1]}'
