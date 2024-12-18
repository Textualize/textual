from typing import NamedTuple

from textual.geometry import Offset


class Selection(NamedTuple):
    """A selected range of lines."""

    start: Offset | None
    """Offset or None for `start`."""
    end: Offset | None
    """Offset or None for `end`."""

    def get_span(self, y: int) -> tuple[int, int] | None:
        """Get the selected span in a given line.

        Args:
            y: Offset of the line.

        Returns:
            A tuple of x start and end offset, or None for no selection.
        """
        start, end = self
        if start is None and end is None:
            # Selection covers everything
            return 0, -1

        if start is not None and end is not None:
            if y < start.y or y > end.y:
                # Outside
                return None
            if y == start.y == end.y:
                # Same line
                return start.x, end.x
            if y == end.y:
                # Last line
                return 0, end.x
            # Remaining lines
            return start.x, -1

        if start is None and end is not None:
            if y == end.y:
                return 0, end.x
            return 0, -1

        if end is None and start is not None:
            if y == start.y:
                return start.x, -1
        return 0, -1
