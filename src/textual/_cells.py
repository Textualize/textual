from typing import Callable

from textual.expand_tabs import get_tab_widths

__all__ = ["cell_len", "cell_width_to_column_index"]


cell_len: Callable[[str], int]
try:
    from rich.cells import cached_cell_len as cell_len
except ImportError:
    from rich.cells import cell_len


def cell_width_to_column_index(line: str, cell_width: int, tab_width: int) -> int:
    """Retrieve the column index corresponding to the given cell width.

    Args:
        line: The line of text to search within.
        cell_width: The cell width to convert to column index.
        tab_width: The tab stop width to expand tabs contained within the line.

    Returns:
        The column corresponding to the cell width.
    """
    column_index = 0
    total_cell_offset = 0
    for part, expanded_tab_width in get_tab_widths(line, tab_width):
        # Check if the click landed on a character within this part.
        for character in part:
            total_cell_offset += cell_len(character)
            if total_cell_offset > cell_width:
                return column_index
            column_index += 1

        # Account for the appearance of the tab character for this part
        total_cell_offset += expanded_tab_width
        # Check if the click falls within the boundary of the expanded tab.
        if total_cell_offset > cell_width:
            return column_index

        column_index += 1

    return len(line)
