"""Provides a utility function and class for creating Markdown-friendly slugs.

The approach to creating slugs is designed to be as close to
GitHub-flavoured Markdown as possible. However, because there doesn't appear
to be any actual documentation for this 'standard', the code here involves
some guesswork and also some pragmatic shortcuts.

Expect this to grow over time.

The main rules used in here at the moment are:

1. Strip all leading and trailing whitespace.
2. Remove all non-lingual characters (emoji, etc).
3. Remove all punctuation and whitespace apart from dash and underscore.
"""

from __future__ import annotations

from collections import defaultdict
from re import compile
from string import punctuation
from typing import Pattern
from urllib.parse import quote

from typing_extensions import Final

WHITESPACE_REPLACEMENT: Final[str] = "-"
"""The character to replace undesirable characters with."""

REMOVABLE: Final[str] = punctuation.replace(WHITESPACE_REPLACEMENT, "").replace("_", "")
"""The collection of characters that should be removed altogether."""

NONLINGUAL: Final[str] = (
    r"\U000024C2-\U0001F251"
    r"\U00002702-\U000027B0"
    r"\U0001F1E0-\U0001F1FF"
    r"\U0001F300-\U0001F5FF"  # Miscellaneous Symbols And Pictographs
    r"\U0001F600-\U0001F64F"  # Emoticons
    r"\U0001F680-\U0001F6FF"  # Transport and Map Symbols
    r"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    r"\u200D"
    r"\u2640-\u2642"
)
"""A string that can be used in a regular expression to remove most non-lingual characters."""

STRIP_RE: Final[Pattern] = compile(f"[{REMOVABLE}{NONLINGUAL}]+")
"""A regular expression for finding all the characters that should be removed."""

WHITESPACE_RE: Final[Pattern] = compile(r"\s")
"""A regular expression for finding all the whitespace and turning it into `REPLACEMENT`."""


def slug(text: str) -> str:
    """Create a Markdown-friendly slug from the given text.

    Args:
        text: The text to generate a slug from.

    Returns:
        A slug for the given text.

    The rules used in generating the slug are based on observations of how
    GitHub-flavoured Markdown works.
    """
    result = text.strip().lower()
    for rule, replacement in (
        (STRIP_RE, ""),
        (WHITESPACE_RE, WHITESPACE_REPLACEMENT),
    ):
        result = rule.sub(replacement, result)
    return quote(result)


class TrackedSlugs:
    """Provides a class for generating tracked slugs.

    While [`slug`][textual._slug.slug] will generate a slug for a given
    string, it does not guarantee that it is unique for a given context. If
    you want to ensure that the same string generates unique slugs (perhaps
    heading slugs within a Markdown document, as an example), use an
    instance of this class to generate them.

    Example:
        ```python
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
        """Initialise the tracked slug object."""
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


VALID_ID_CHARACTERS = frozenset("abcdefghijklmnopqrstuvwxyz0123456789-")


def slug_for_tcss_id(text: str) -> str:
    """Produce a slug usable as a TCSS id from the given text.

    Args:
        text: Text.

    Returns:
        A slugified version of text suitable for use as a TCSS id.
    """
    is_valid = VALID_ID_CHARACTERS.__contains__
    slug = "".join(
        (character if is_valid(character) else "{:x}".format(ord(character)))
        for character in text.casefold().replace(" ", "-")
    )
    if not slug:
        return "_"
    if slug[0].isdecimal():
        return f"_{slug}"
    return slug
