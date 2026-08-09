"""Word segmentation helpers.

This module provides an optional-dependency structure for word segmentation.
If the third-party `regex` package is installed, it is used for more accurate
Unicode-aware word matching (including marks and a broader range of word
characters). Otherwise the implementation falls back to Python's standard
``re`` module.

In the future this can be extended to use a full UAX #29 word-boundary
implementation (e.g. ``regex`` with ``\b{wb}`` or ``uniseg``).
"""

from __future__ import annotations

import re

try:
    import regex as _regex_module  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    _regex_module = None

if _regex_module is not None:
    # Use Unicode character properties when the regex package is available.
    # This includes letters (L), numbers (N), and marks (M) so that combining
    # characters stay attached to their base characters.
    _WORD_OR_URL_RE = _regex_module.compile(
        r"(?:https?|ftp)://\S+|[\p{L}\p{N}\p{M}'’-]+",
        _regex_module.UNICODE,
    )
else:
    _WORD_OR_URL_RE = re.compile(
        r"(?:https?|ftp)://\S+|[\w'’-]+",
        re.UNICODE,
    )


def get_word_offsets(text: str, flat_offset: int) -> tuple[int, int] | None:
    """Return the start and end offsets of the word containing the given offset.

    Args:
        text: The text to search.
        flat_offset: A character offset within the text.

    Returns:
        A tuple of (start, end) offsets, or ``None`` if no word was found at the offset.
    """
    if not text or flat_offset < 0 or flat_offset > len(text):
        return None

    # Clamp an offset that is exactly at the end of the text to the last character.
    if flat_offset == len(text):
        flat_offset = max(0, len(text) - 1)

    for match in _WORD_OR_URL_RE.finditer(text):
        start, end = match.span()
        if start <= flat_offset < end:
            return start, end

    return None
