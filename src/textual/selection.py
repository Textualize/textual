from __future__ import annotations

from typing import NamedTuple

from textual.geometry import Offset


class Selection(NamedTuple):
    """A selected range of lines."""

    start: Offset | None
    """Offset or None for `start`."""
    end: Offset | None
    """Offset or None for `end`."""

    @classmethod
    def from_offsets(cls, offset1: Offset, offset2: Offset) -> Selection:
        """Create selection from 2 offsets.

        Args:
            offset1: First offset.
            offset2: Second offset.

        Returns:
            New Selection.
        """
        offsets = sorted([offset1, offset2], key=(lambda offset: (offset.y, offset.x)))
        return cls(*offsets)

    def extract(self, text: str) -> str:
        """Extract selection from text.

        Args:
            text: Raw text pulled from widget.

        Returns:
            Extracted text.
        """
        lines = text.splitlines()
        if not lines:
            return ""
        if self.start is None:
            start_line = 0
            start_offset = 0
        else:
            start_line, start_offset = self.start.transpose

        if self.end is None:
            end_line = len(lines) - 1
            end_offset = len(lines[end_line])
        else:
            end_line, end_offset = self.end.transpose
        end_line = min(len(lines), end_line)

        if start_line == end_line:
            return lines[start_line][start_offset:end_offset]

        selection: list[str] = []
        selected_lines = lines[start_line:end_line]
        if len(selected_lines) >= 2:
            first_line, *mid_lines, last_line = selected_lines
            selection.append(first_line[start_offset:])
            selection.extend(mid_lines)
            selection.append(last_line[: end_offset + 1])
        else:
            return lines[start_line][start_offset:end_offset]
        return "\n".join(selection)

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
            if y == start.y and start.y == end.y:
                # Same line
                return start.x, end.x
            if y == end.y:
                # Last line
                return 0, end.x
            if y == start.y:
                return start.x, -1
            # Remaining lines
            return 0, -1

        if start is None and end is not None:
            if y == end.y:
                return 0, end.x
            if y > end.y:
                return None
            return 0, -1

        if end is None and start is not None:
            if y == start.y:
                return start.x, -1
            if y > start.y:
                return 0, -1
            return None
        return 0, -1


SELECT_ALL = Selection(None, None)
