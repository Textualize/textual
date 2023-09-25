from __future__ import annotations

import re

from rich.cells import cell_len

_TABS_SPLITTER_RE = re.compile(r"(.*?\t|.+?$)")


def expand_tabs_inline(line: str, tab_size: int = 4) -> str:
    """Expands tabs, taking into account double cell characters.

    Args:
        line: The text to expand tabs in.
        tab_size: Number of cells in a tab.
    Returns:
        New string with tabs replaced with spaces.
    """
    if "\t" not in line:
        return line
    new_line_parts: list[str] = []
    add_part = new_line_parts.append
    cell_position = 0
    parts = _TABS_SPLITTER_RE.findall(line)

    for part in parts:
        if part.endswith("\t"):
            part = f"{part[:-1]} "
            cell_position += cell_len(part)
            tab_remainder = cell_position % tab_size
            if tab_remainder:
                spaces = tab_size - tab_remainder
                part += spaces * " "
        add_part(part)

    return "".join(new_line_parts)


if __name__ == "__main__":
    print(expand_tabs_inline("\tbar"))
    print(expand_tabs_inline("1\tbar"))
    print(expand_tabs_inline("12\tbar"))
    print(expand_tabs_inline("123\tbar"))
    print(expand_tabs_inline("1234\tbar"))
    print(expand_tabs_inline("💩\tbar"))
    print(expand_tabs_inline("💩💩\tbar"))
    print(expand_tabs_inline("💩💩💩\tbar"))
    print(expand_tabs_inline("F💩\tbar"))
    print(expand_tabs_inline("F💩O\tbar"))
