"""
BiDi (Bidirectional) text support for RTL languages like Hebrew and Arabic.

This module provides utilities for applying the Unicode BiDi algorithm to text,
ensuring proper display of right-to-left (RTL) languages in terminal applications.

The `python-bidi` library is an optional dependency. If not installed, BiDi
processing will be silently skipped.
"""

from __future__ import annotations

import unicodedata
from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.content import Content, Span

# RTL BiDi character types from Unicode
RTL_BIDI_TYPES = frozenset({"R", "AL", "RLE", "RLO", "RLI"})

# Try to import python-bidi
try:
    from bidi.algorithm import get_display as _bidi_get_display

    BIDI_AVAILABLE = True
except ImportError:
    BIDI_AVAILABLE = False

    def _bidi_get_display(text: str, **kwargs: object) -> str:
        """Fallback when python-bidi is not installed."""
        return text


@lru_cache(maxsize=512)
def contains_rtl(text: str) -> bool:
    """Check if text contains any RTL (right-to-left) characters.

    This function detects Hebrew, Arabic, and other RTL scripts by checking
    the Unicode bidirectional property of each character.

    Args:
        text: The text to check.

    Returns:
        True if the text contains RTL characters, False otherwise.
    """
    if not text:
        return False

    for char in text:
        bidi_class = unicodedata.bidirectional(char)
        if bidi_class in RTL_BIDI_TYPES:
            return True
    return False


def get_display(text: str) -> str:
    """Apply the Unicode BiDi algorithm to reorder text for display.

    Terminals render characters left-to-right, but RTL languages need
    character reordering for correct visual display. This function applies
    the Unicode BiDi algorithm to produce the correct visual ordering.

    Args:
        text: The logical text to reorder.

    Returns:
        The text reordered for visual display.
    """
    if not BIDI_AVAILABLE or not text:
        return text
    return _bidi_get_display(text)


def get_display_with_mapping(text: str) -> tuple[str, list[int]]:
    """Apply BiDi algorithm and return both display text and character mapping.

    This function not only reorders the text but also provides a mapping from
    display positions to original positions. This is essential for preserving
    style spans when text is reordered.

    Args:
        text: The logical text to reorder.

    Returns:
        A tuple of (display_text, mapping) where mapping[display_pos] gives
        the original position of the character at display_pos.
    """
    if not BIDI_AVAILABLE or not text:
        return text, list(range(len(text)))

    # python-bidi doesn't provide direct mapping, so we need to compute it
    # by tracking unique character positions
    if not contains_rtl(text):
        return text, list(range(len(text)))

    # Create unique markers for each position to track reordering
    # This approach handles duplicate characters correctly
    display = _bidi_get_display(text)

    # Build mapping by finding where each character moved
    # We use a greedy matching approach from left to right
    mapping: list[int] = []
    used_positions: set[int] = set()

    for display_char in display:
        # Find the leftmost unused position in original text with this char
        for orig_pos, orig_char in enumerate(text):
            if orig_pos not in used_positions and orig_char == display_char:
                mapping.append(orig_pos)
                used_positions.add(orig_pos)
                break
        else:
            # Character not found (shouldn't happen with valid BiDi)
            mapping.append(len(mapping))

    return display, mapping


def remap_spans(
    spans: list[Span], mapping: list[int], display_length: int
) -> list[Span]:
    """Remap style spans after BiDi reordering.

    When text is reordered by the BiDi algorithm, style spans must be
    recalculated to apply to the correct character positions in the
    display order.

    Args:
        spans: Original spans with positions in logical order.
        mapping: Mapping from display positions to original positions.
        display_length: Length of the display text.

    Returns:
        New spans with positions adjusted for display order.
    """
    from textual.content import Span as SpanClass

    if not spans or not mapping:
        return spans

    # Create reverse mapping: original_pos -> display_pos
    reverse_mapping: dict[int, int] = {}
    for display_pos, orig_pos in enumerate(mapping):
        if orig_pos not in reverse_mapping:
            reverse_mapping[orig_pos] = display_pos

    new_spans: list[Span] = []
    for span in spans:
        start, end, style = span.start, span.end, span.style

        # Find all display positions that map to the span's range
        display_positions: list[int] = []
        for display_pos, orig_pos in enumerate(mapping):
            if start <= orig_pos < end:
                display_positions.append(display_pos)

        if not display_positions:
            continue

        # Create contiguous spans from the display positions
        display_positions.sort()

        # Group into contiguous ranges
        ranges: list[tuple[int, int]] = []
        range_start = display_positions[0]
        range_end = display_positions[0] + 1

        for pos in display_positions[1:]:
            if pos == range_end:
                range_end = pos + 1
            else:
                ranges.append((range_start, range_end))
                range_start = pos
                range_end = pos + 1
        ranges.append((range_start, range_end))

        # Create a span for each contiguous range
        for new_start, new_end in ranges:
            new_spans.append(SpanClass(new_start, new_end, style))

    return new_spans


def apply_bidi_to_content(content: Content) -> Content:
    """Apply BiDi algorithm to Content, preserving style spans.

    This function applies the Unicode BiDi algorithm to reorder the text
    for visual display while preserving all style information (colors,
    formatting, etc.).

    Args:
        content: The Content object with logical text order.

    Returns:
        A new Content object with text reordered for display, spans adjusted.
    """
    from textual.content import Content as ContentClass

    text = content.plain
    spans = list(content.spans)

    # Quick path: no RTL characters
    if not contains_rtl(text):
        return content

    # Quick path: BiDi not available
    if not BIDI_AVAILABLE:
        return content

    # Apply BiDi with mapping
    display_text, mapping = get_display_with_mapping(text)

    # If text didn't change, return as-is
    if display_text == text:
        return content

    # Remap spans to new positions
    new_spans = remap_spans(spans, mapping, len(display_text))

    return ContentClass(display_text, new_spans, strip_control_codes=False)


def apply_bidi_to_line(text: str) -> str:
    """Apply BiDi algorithm to a single line of text.

    This is a simpler version of apply_bidi_to_content for cases where
    style spans are not needed, such as plain text or TextArea content.

    Args:
        text: The logical text to reorder.

    Returns:
        The text reordered for visual display.
    """
    if not contains_rtl(text):
        return text
    return get_display(text)
