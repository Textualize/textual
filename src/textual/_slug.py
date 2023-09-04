"""Provides a utility function and class for creating Markdown-friendly slugs.

The approach to creating slugs is designed to be as close to
GitHub-flavoured Markdown as possible.
"""

from __future__ import annotations

from collections import defaultdict
from re import compile
from string import punctuation
from typing import Pattern

from typing_extensions import Final

REPLACEMENT: Final[str] = "-"
"""The character to replace undesirable characters with."""

REMOVABLE: Final[str] = punctuation.replace(REPLACEMENT, "").replace("_", "")
"""The collection of characters that should be removed altogether."""

STRIP_RE: Final[Pattern] = compile(f"[{REMOVABLE}]+")
"""A regular expression for finding all the characters that should be removed."""

SIMPLIFY_RE: Final[Pattern] = compile(rf"[{REPLACEMENT}\s]+")
"""A regular expression for finding all the characters that can be turned into a `REPLACEMENT`."""


def slug(text: str) -> str:
    """Create a Markdown-friendly slug from the given text.

    Args:
        text: The text to generate a slug from.

    Returns:
        A slug for the given text.
    """
    result = text.strip().lower()
    for rule, replacement in (
        (STRIP_RE, ""),
        (SIMPLIFY_RE, REPLACEMENT),
    ):
        result = rule.sub(replacement, result)
    return result


class TrackedSlugs:
    """Provides a class for generating tracked slugs.

    While [`slug`][textual._slug.slug] will generate a slug for a given
    string, it does not guarantee that it is unique for a given context. If
    you want to ensure that the same string generates unique slugs (perhaps
    heading slugs within a Markdown document, as an example), use an
    instance of this class to generate them.

    Example:
        ```Python
        >>> slug("hello world")
        'hello-world'
        >>> slug("hello world")
        'hello-world'
        >>> unique = TrackedSlugs()
        >>> unique.slug("hello world")
        'hello-world'
        >>> unique.slug("hello world")
        'hello-world-1'
        ```
    """

    def __init__(self) -> None:
        self._used: defaultdict[str, int] = defaultdict(int)
        """Keeps track of how many times a particular slug has been used."""

    def slug(self, text: str) -> str:
        """Create a Markdown-friendly unique slug from the given text.

        Args:
            text: The text to generate a slug from.

        Returns:
            A slug for the given text.
        """
        slugged = slug(text)
        used = self._used[slugged]
        self._used[slugged] += 1
        if used:
            slugged = f"{slugged}-{used}"
        return slugged


if __name__ == "__main__":
    for text in ("Hello", "Hello world", "Hello -- world!!!", "Hello, World!"):
        print(f"'{text}' -> '{slug(text)}'")

    print("")
    slugger = TrackedSlugs()
    for _ in range(10):
        print(slugger.slug("Hello, World!"))
