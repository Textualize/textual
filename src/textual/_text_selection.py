"""Text selection utilities.

This module provides helpers for selecting words and paragraphs from a widget's
text content. The default word segmentation uses the pluggable word-segmentation
module (`textual._word_segmentation`). Widgets can override the selection methods
on `Widget` for more sophisticated behavior.
"""

from __future__ import annotations

import re

from textual._word_segmentation import get_word_offsets
from textual.geometry import Offset
from textual.selection import Selection


def _split_lines(text: str) -> list[tuple[str, int]]:
    """Split text into lines, preserving the exact width of each newline.

    This is like ``str.splitlines()`` but also returns the width of the line
    ending (``\r\n`` is 2, ``\n`` or ``\r`` is 1, end-of-text is 0).

    Args:
        text: The text to split.

    Returns:
        A list of ``(line_text, newline_width)`` pairs.
    """
    if not text:
        return []

    lines: list[tuple[str, int]] = []
    start = 0
    for match in re.finditer(r"\r\n|\r|\n", text):
        line_end = match.start()
        newline_width = len(match.group())
        lines.append((text[start:line_end], newline_width))
        start = match.end()

    # Only add a final line if there is content after the last newline.
    if start < len(text):
        lines.append((text[start:], 0))

    return lines


def _flat_offset_to_offset(text: str, flat_offset: int) -> Offset:
    """Convert a flat character offset into a line/character Offset.

    Args:
        text: The text being selected.
        flat_offset: A character offset in the text.

    Returns:
        An Offset where x is the character offset on the line and y is the line index.
    """
    if flat_offset <= 0:
        return Offset(0, 0)

    lines = _split_lines(text)
    position = 0
    for y, (line, newline_width) in enumerate(lines):
        line_end = position + len(line)
        if flat_offset <= line_end:
            return Offset(flat_offset - position, y)

        next_position = line_end + newline_width
        if flat_offset < next_position:
            # The offset falls inside a newline; clamp to the end of the line.
            return Offset(len(line), y)

        position = next_position

    # Past the end of the text; clamp to the last position.
    if lines:
        last_line, _ = lines[-1]
        return Offset(len(last_line), len(lines) - 1)
    return Offset(0, 0)


def get_word_selection(text: str, offset: Offset) -> Selection | None:
    """Get a Selection for the word at the given offset.

    Args:
        text: The text to search.
        offset: A line/character offset within the text.

    Returns:
        A Selection for the word, or None if no word was found.
    """
    lines = _split_lines(text)
    flat_offset = sum(
        len(line) + newline_width for line, newline_width in lines[: offset.y]
    ) + offset.x
    word_offsets = get_word_offsets(text, flat_offset)
    if word_offsets is None:
        return None

    start, end = word_offsets
    return Selection.from_offsets(
        _flat_offset_to_offset(text, start),
        _flat_offset_to_offset(text, end),
    )


def get_paragraph_offsets(text: str, flat_offset: int) -> tuple[int, int] | None:
    """Return the start and end offsets of the paragraph containing the given offset.

    Paragraphs are separated by blank lines.

    Args:
        text: The text to search.
        flat_offset: A character offset within the text.

    Returns:
        A tuple of (start, end) offsets, or None if no paragraph was found.
    """
    if not text or flat_offset < 0 or flat_offset > len(text):
        return None

    lines_info = _split_lines(text)
    if not lines_info:
        return None

    lines = [line for line, _ in lines_info]

    # Find the line containing the offset.
    line_index = 0
    position = 0
    for i, (line, newline_width) in enumerate(lines_info):
        line_end = position + len(line)
        if position <= flat_offset <= line_end:
            line_index = i
            break
        position = line_end + newline_width

    # Expand to paragraph boundaries (blank lines).
    start_line = line_index
    while start_line > 0 and lines[start_line - 1] != "":
        start_line -= 1

    end_line = line_index
    while end_line < len(lines) - 1 and lines[end_line + 1] != "":
        end_line += 1

    start = sum(
        len(line) + newline_width
        for line, newline_width in lines_info[:start_line]
    )
    end = sum(
        len(line) + newline_width
        for line, newline_width in lines_info[:end_line]
    ) + len(lines_info[end_line][0])
    return start, end


def get_paragraph_selection(text: str, offset: Offset) -> Selection | None:
    """Get a Selection for the paragraph at the given offset.

    Args:
        text: The text to search.
        offset: A line/character offset within the text.

    Returns:
        A Selection for the paragraph, or None if no paragraph was found.
    """
    lines_info = _split_lines(text)
    flat_offset = sum(
        len(line) + newline_width for line, newline_width in lines_info[: offset.y]
    ) + offset.x
    paragraph_offsets = get_paragraph_offsets(text, flat_offset)
    if paragraph_offsets is None:
        return None

    start, end = paragraph_offsets
    return Selection.from_offsets(
        _flat_offset_to_offset(text, start),
        _flat_offset_to_offset(text, end),
    )
