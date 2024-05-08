from __future__ import annotations

import re

from rich.cells import cell_len
from rich.text import Text

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


def expand_text_tabs_from_widths(line: Text, tab_widths: list[int]) -> Text:
    """Expand tabs to the widths defined in the `tab_widths` list.

    This will return a new Text instance with tab characters expanded into a
    number of spaces. Each time a tab is encountered, it's expanded into the
    next integer encountered in the `tab_widths` list. Consequently, the length
    of `tab_widths` should match the number of tab characters in `line`.

    Args:
        line: The `Text` instance to expand tabs in.
        tab_widths: The widths to expand tabs to.

    Returns:
        A new text instance with tab characters converted to spaces.
    """
    if "\t" not in line.plain:
        return line

    parts = line.split("\t", include_separator=True)
    tab_widths_iter = iter(tab_widths)

    new_parts: list[Text] = []
    append_part = new_parts.append
    for part in parts:
        if part.plain.endswith("\t"):
            part._text[-1] = part._text[-1][:-1] + " "
            spaces = next(tab_widths_iter)
            part.extend_style(spaces - 1)
        append_part(part)

    return Text("", end="").join(new_parts)


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
