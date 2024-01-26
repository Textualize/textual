from __future__ import annotations

import re

from rich.cells import cell_len

_TABS_SPLITTER_RE = re.compile(r"(.*?\t|.+?$)")


def get_tab_widths(line: str, tab_size: int = 4) -> list[tuple[str, int]]:
    """Splits a string line into tuples (str, int).

    Each tuple represents a section of the line which precedes a tab character.
    The string is the string text that appears before the tab character (excluding the tab).
    The integer is the width that the tab character is expanded to.

    Args:
        line: The text to expand tabs in.
        tab_size: Number of cells in a tab.

    Returns:
        A list of tuples representing the line split on tab characters,
            and the widths of the tabs after tab expansion is applied.

    """

    parts: list[tuple[str, int]] = []
    add_part = parts.append
    cell_position = 0
    matches = _TABS_SPLITTER_RE.findall(line)

    for match in matches:
        expansion_width = 0
        if match.endswith("\t"):
            # Remove the tab, and check the width of the rest of the line.
            match = match[:-1]
            cell_position += cell_len(match)

            # Now move along the line by the width of the tab.
            tab_remainder = cell_position % tab_size
            expansion_width = tab_size - tab_remainder
            cell_position += expansion_width

        add_part((match, expansion_width))

    return parts


def expand_tabs_inline(line: str, tab_size: int = 4) -> str:
    """Expands tabs, taking into account double cell characters.

    Args:
        line: The text to expand tabs in.
        tab_size: Number of cells in a tab.
    Returns:
        New string with tabs replaced with spaces.
    """
    tab_widths = get_tab_widths(line, tab_size)
    return "".join(
        [part + expansion_width * " " for part, expansion_width in tab_widths]
    )


if __name__ == "__main__":
    print(expand_tabs_inline("\tbar"))
    print(expand_tabs_inline("\tbar\t"))
    print(expand_tabs_inline("1\tbar"))
    print(expand_tabs_inline("12\tbar"))
    print(expand_tabs_inline("123\tbar"))
    print(expand_tabs_inline("1234\tbar"))
    print(expand_tabs_inline("💩\tbar"))
    print(expand_tabs_inline("💩💩\tbar"))
    print(expand_tabs_inline("💩💩💩\tbar"))
    print(expand_tabs_inline("F💩\tbar"))
    print(expand_tabs_inline("F💩O\tbar"))
