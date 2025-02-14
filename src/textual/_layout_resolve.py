from __future__ import annotations

from fractions import Fraction
from typing import Sequence, cast

from typing_extensions import Protocol


class EdgeProtocol(Protocol):
    """Any object that defines an edge (such as Layout)."""

    # Size of edge in cells, or None for no fixed size
    size: int | None
    # Portion of flexible space to use if size is None
    fraction: int
    # Minimum size for edge, in cells
    min_size: int


def layout_resolve(total: int, edges: Sequence[EdgeProtocol]) -> list[int]:
    """Divide total space to satisfy size, fraction, and min_size, constraints.

    The returned list of integers should add up to total in most cases, unless it is
    impossible to satisfy all the constraints. For instance, if there are two edges
    with a minimum size of 20 each and `total` is 30 then the returned list will be
    greater than total. In practice, this would mean that a Layout object would
    clip the rows that would overflow the screen height.

    Args:
        total: Total number of characters.
        edges: Edges within total space.

    Returns:
        Number of characters for each edge.
    """
    # Size of edge or None for yet to be determined
    sizes = [(edge.size or None) for edge in edges]

    if None not in sizes:
        # No flexible edges
        return cast("list[int]", sizes)

    # Get flexible edges and index to map these back on to sizes list
    flexible_edges = [
        (index, edge)
        for index, (size, edge) in enumerate(zip(sizes, edges))
        if size is None
    ]
    # Remaining space in total
    remaining = total - sum([size or 0 for size in sizes])
    if remaining <= 0:
        # No room for flexible edges
        return [
            ((edge.min_size or 1) if size is None else size)
            for size, edge in zip(sizes, edges)
        ]

    # Get the total fraction value for all flexible edges
    total_flexible = sum([(edge.fraction or 1) for _, edge in flexible_edges])
    while flexible_edges:
        # Calculate number of characters in a ratio portion
        portion = Fraction(remaining, total_flexible)

        # If any edges will be less than their minimum, replace size with the minimum
        for flexible_index, (index, edge) in enumerate(flexible_edges):
            if portion * edge.fraction < edge.min_size:
                # This flexible edge will be smaller than its minimum size
                # We need to fix the size and redistribute the outstanding space
                sizes[index] = edge.min_size
                remaining -= edge.min_size
                total_flexible -= edge.fraction or 1
                del flexible_edges[flexible_index]
                # New fixed size will invalidate calculations, so we need to repeat the process
                break
        else:
            # Distribute flexible space and compensate for rounding error
            # Since edge sizes can only be integers we need to add the remainder
            # to the following line
            remainder = Fraction(0)
            for index, edge in flexible_edges:
                sizes[index], remainder = divmod(portion * edge.fraction + remainder, 1)
            break

    # Sizes now contains integers only
    return cast("list[int]", sizes)
