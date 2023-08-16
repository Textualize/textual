from __future__ import annotations


def _sort_ascending(
    start: tuple[int, int], end: tuple[int, int]
) -> tuple[tuple[int, int], tuple[int, int]]:
    """Given a range, return a new range (x, y) such
    that x <= y which covers the same characters."""
    if start > end:
        return end, start
    return start, end
