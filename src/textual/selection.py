from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from textual.geometry import Offset
    from textual.widget import Widget


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
            start_line_index = 0
            start_offset = 0
        else:
            start_line_index, start_offset = self.start.transpose

        if self.end is None:
            end_line = len(lines)
            end_offset = len(lines[-1])
        else:
            end_line, end_offset = self.end.transpose
        end_line = min(len(lines), end_line)

        if start_line_index == end_line:
            return lines[start_line_index][start_offset:end_offset]

        selection: list[str] = []
        selected_lines = lines[start_line_index : end_line + 1]
        if len(selected_lines) >= 2:
            first_line, *mid_lines, last_line = selected_lines
            selection.append(first_line[start_offset:])
            selection.extend(mid_lines)
            selection.append(last_line[:end_offset])
        else:
            try:
                selection.append(lines[start_line_index][start_offset:end_offset])
            except IndexError:
                pass
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


class SelectState(NamedTuple):
    """An object which describes the current select state."""

    pointer_offset: Offset
    """The current mouse position, in screen space."""

    start_widget: Widget
    """The widget under the mouse when selection started."""

    select_container: Widget | None = None
    """The scrolling container from the initial MouseDown"""

    start_widget_offset: Offset | None = None
    """The offset of the widget when the selection started"""

    start_content_offset: Offset | None = None
    """The offset within the start widget content."""

    end_widget: Widget | None = None
    """The widget currently under the mouse."""

    end_content_offset: Offset | None = None
    """The offset within the end_widget content."""

    @property
    def content_offsets(self) -> tuple[Offset, Offset]:
        """Get the content offset in select order."""
        start_offset = self.start_content_offset
        end_offset = self.end_content_offset
        assert start_offset is not None
        assert end_offset is not None
        if end_offset.transpose < start_offset.transpose:
            start_offset, end_offset = end_offset, start_offset
        return start_offset, end_offset

    @property
    def is_single_widget(self) -> bool:
        """Is the select within a single widget?"""
        return self.start_widget is not None and self.start_widget is self.end_widget

    @property
    def has_content_offsets(self) -> bool:
        """Are both content offsets present?"""
        return (
            self.start_content_offset is not None
            and self.end_content_offset is not None
        )
