from typing import Callable

from textual.expand_tabs import expand_tabs_inline

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
    total_cell_offset = 0
    for column_index, character in enumerate(line):
        total_cell_offset += cell_len(expand_tabs_inline(character, tab_width))
        if total_cell_offset >= cell_width + 1:
            return column_index
    return len(line)
