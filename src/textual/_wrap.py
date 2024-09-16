from __future__ import annotations

import re
from typing import Iterable

from rich.cells import get_character_cell_size

from textual._cells import cell_len
from textual._loop import loop_last
from textual.expand_tabs import get_tab_widths

re_chunk = re.compile(r"\S+\s*|\s+")


def chunks(text: str) -> Iterable[tuple[int, int, str]]:
    """Yields each "chunk" from the text as a tuple containing (start_index, end_index, chunk_content).
    A "chunk" in this context refers to a word and any whitespace around it.

    Args:
        text: The text to split into chunks.

    Returns:
        Yields tuples containing the start, end and content for each chunk.
    """
    end = 0
    while (chunk_match := re_chunk.match(text, end)) is not None:
        start, end = chunk_match.span()
        chunk = chunk_match.group(0)
        yield start, end, chunk


def compute_wrap_offsets(
    text: str,
    width: int,
    tab_size: int,
    fold: bool = True,
    precomputed_tab_sections: list[tuple[str, int]] | None = None,
) -> list[int]:
    """Given a string of text, and a width (measured in cells), return a list
    of codepoint indices which the string should be split at in order for it to fit
    within the given width.

    Args:
        text: The text to examine.
        width: The available cell width.
        tab_size: The tab stop width.
        fold: If True, words longer than `width` will be folded onto a new line.
        precomputed_tab_sections: The output of `get_tab_widths` can be passed here directly,
            to prevent us from having to recompute the value.

    Returns:
        A list of indices to break the line at.
    """
    tab_size = min(tab_size, width)
    if precomputed_tab_sections:
        tab_sections = precomputed_tab_sections
    else:
        tab_sections = get_tab_widths(text, tab_size)

    break_positions: list[int] = []  # offsets to insert the breaks at
    append = break_positions.append
    cell_offset = 0
    _cell_len = cell_len

    tab_section_index = 0
    cumulative_width = 0
    cumulative_widths: list[int] = []  # prefix sum of tab widths for each codepoint
    record_widths = cumulative_widths.extend

    for last, (tab_section, tab_width) in loop_last(tab_sections):
        # add 1 since the \t character is stripped by get_tab_widths
        section_codepoint_length = len(tab_section) + int(bool(tab_width))
        widths = [cumulative_width] * section_codepoint_length
        record_widths(widths)
        cumulative_width += tab_width
        if last:
            cumulative_widths.append(cumulative_width)

    for start, end, chunk in chunks(text):
        chunk_width = _cell_len(chunk)  # this cell len excludes tabs completely
        tab_width_before_start = cumulative_widths[start]
        tab_width_before_end = cumulative_widths[end]
        chunk_tab_width = tab_width_before_end - tab_width_before_start
        chunk_width += chunk_tab_width
        remaining_space = width - cell_offset
        chunk_fits = remaining_space >= chunk_width

        if chunk_fits:
            # Simplest case - the word fits within the remaining width for this line.
            cell_offset += chunk_width
        else:
            # Not enough space remaining for this word on the current line.
            if chunk_width > width:
                # The word doesn't fit on any line, so we must fold it
                if fold:
                    _get_character_cell_size = get_character_cell_size
                    lines: list[list[str]] = [[]]

                    append_new_line = lines.append
                    append_to_last_line = lines[-1].append

                    total_width = 0
                    for character in chunk:
                        if character == "\t":
                            # Tab characters have dynamic width, so look it up
                            cell_width = tab_sections[tab_section_index][1]
                            tab_section_index += 1
                        else:
                            cell_width = _get_character_cell_size(character)

                        if total_width + cell_width > width:
                            append_new_line([character])
                            append_to_last_line = lines[-1].append
                            total_width = cell_width
                        else:
                            append_to_last_line(character)
                            total_width += cell_width

                    folded_word = ["".join(line) for line in lines]
                    for last, line in loop_last(folded_word):
                        if start:
                            append(start)
                        if last:
                            # Since cell_len ignores tabs, we need to check the width
                            # of the tabs in this line. The width of tabs within the
                            # line is computed by taking the difference between the
                            # cumulative width of tabs up to the end of the line and the
                            # cumulative width of tabs up to the start of the line.
                            line_tab_widths = (
                                cumulative_widths[start + len(line)]
                                - cumulative_widths[start]
                            )
                            cell_offset = _cell_len(line) + line_tab_widths
                        else:
                            start += len(line)
                else:
                    # Folding isn't allowed, so crop the word.
                    if start:
                        append(start)
                    cell_offset = chunk_width
            elif cell_offset and start:
                # The word doesn't fit within the remaining space on the current
                # line, but it *can* fit on to the next (empty) line.
                append(start)
                cell_offset = chunk_width

    return break_positions
