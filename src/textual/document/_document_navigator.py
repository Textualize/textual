"""Cursor navigation in the TextArea is "wrapping-aware".

Although the cursor location (the selection) is represented as a location
in the raw document, when you actually *move* the cursor, it must take wrapping
into account (otherwise things start to look really confusing to the user where
wrapping is involved).

Your cursor visually moves through the wrapped version of the document, rather
than the raw document. So, for example, pressing down on the keyboard
may move your cursor to a position further along the current line,
rather than on to the next line in the raw document.

The class manages this behaviour.

Given a cursor location in the unwrapped document, and a cursor movement action,
this class can inform us of the destination the cursor will move to considering
the current wrapping width and document content.

For this to work correctly, the wrapped_document and document must be synchronised.
This means that if you make an edit to the document, you *must* then update the
wrapped document, and *then* you may query the document navigator.

Naming conventions:

A line "wrapped section" refers to a portion of the line accounting for wrapping.
For example the line "ABCDEF" when wrapped at width 3 will result in 2 sections:
"ABC" and "DEF".

A "wrap offset" is an integer representing the index at which wrapping occurs in a line.
In "ABCDEF" with wrapping at width 3, there is a single wrap offset of 3.
"""

import re
from bisect import bisect, bisect_left, bisect_right
from typing import Any, Sequence

from textual._cells import cell_len
from textual.document._document import Location
from textual.document._wrapped_document import WrappedDocument
from textual.geometry import clamp


class DocumentNavigator:
    def __init__(self, wrapped_document: WrappedDocument) -> None:
        """Create a DocumentNavigator.

        Args:
            wrapped_document: The WrappedDocument to be used when making navigation decisions.
        """
        self._wrapped_document = wrapped_document
        self._document = wrapped_document.document

        self._word_pattern = re.compile(r"(?<=\W)(?=\w)|(?<=\w)(?=\W)")
        """Compiled regular expression for what we consider to be a 'word'."""

        self.last_x_offset = 0
        """Remembers the last x offset (cell width) the cursor was moved horizontally to,
        so that it can be restored on vertical movement where possible."""

    def is_start_of_document_line(self, location: Location) -> bool:
        """True when the location is at the start of the first document line.

        Args:
            location: The location to check.

        Returns:
             True if the location is at column index 0.
        """
        return location[1] == 0

    def is_start_of_wrapped_line(self, location: Location) -> bool:
        """True when the location is at the start of the first wrapped line.

        Args:
            location: The location to check.

        Returns:
             True if the location is at column index 0.
        """
        if self.is_start_of_document_line(location):
            return True

        row, column = location
        wrap_offsets = self._wrapped_document.get_offsets(row)
        return index(wrap_offsets, column) != -1

    def is_end_of_document_line(self, location: Location) -> bool:
        """True if the location is at the end of a line in the document."""
        row, column = location
        row_length = len(self._document[row])
        return column == row_length

    def is_end_of_wrapped_line(self, location: Location) -> bool:
        """True if the location is at the end of a wrapped line."""
        if self.is_end_of_document_line(location):
            return True

        row, column = location
        wrap_offsets = self._wrapped_document.get_offsets(row)
        return index(wrap_offsets, column - 1) != -1

    def is_first_document_line(self, location: Location) -> bool:
        return location[0] == 0

    def is_first_wrapped_line(self, location: Location) -> bool:
        # Ensure that the column index of the location is less (or equal to?!?!) than
        # the first value in the wrap offsets.
        if not self.is_first_document_line(location):
            return False

        row, column = location
        wrap_offsets = self._wrapped_document.get_offsets(row)

        if not wrap_offsets:
            return True

        if column < wrap_offsets[0]:
            return True
        return False

    def is_last_document_line(self, location: Location) -> bool:
        """True when the location is on the last line of the document."""
        return location[0] == self._document.line_count - 1

    def is_last_wrapped_line(self, location: Location) -> bool:
        if not self.is_last_document_line(location):
            return False

        row, column = location
        wrap_offsets = self._wrapped_document.get_offsets(row)

        if not wrap_offsets:
            return True

        if column >= wrap_offsets[-1]:
            return True
        return False

    def is_start_of_document(self, location: Location) -> bool:
        """True if and only if the cursor is at location (0, 0)"""
        return location == (0, 0)

    def is_end_of_document(self, location: Location) -> bool:
        return self.is_last_document_line(location) and self.is_end_of_document_line(
            location
        )

    def left(self, location: Location) -> Location:
        if location == (0, 0):
            return 0, 0

        row, column = location
        length_of_row_above = len(self._document[row - 1])
        target_row = row if column != 0 else row - 1
        target_column = column - 1 if column != 0 else length_of_row_above
        return target_row, target_column

    def right(self, location: Location) -> Location:
        if self.is_end_of_document(location):
            return location
        row, column = location
        is_end_of_line = self.is_end_of_document_line(location)
        target_row = row + 1 if is_end_of_line else row
        target_column = 0 if is_end_of_line else column + 1
        return target_row, target_column

    def get_location_above(self, location: Location, tab_width: int) -> Location:
        """Get the location up from the given location in the wrapped document."""

        # Moving up from a position on the first visual line moves us to the start.
        if self.is_first_wrapped_line(location):
            return 0, 0

        # Get the wrap offsets of the current line.
        line_index, column_index = location
        wrap_offsets = self._wrapped_document.get_offsets(line_index)
        section_start_columns = [0, *wrap_offsets]

        # We need to find the insertion point to determine which section index we're
        # on within the current line. When we know the section index, we can use it
        # to find the section which sits above it.
        section_index = bisect_right(wrap_offsets, column_index)
        offset_within_section = column_index - section_start_columns[section_index]
        wrapped_line = self._wrapped_document.get_sections(line_index)
        section = wrapped_line[section_index]

        # Convert that cursor offset to a cell (visual) offset
        current_visual_offset = cell_len(section[:offset_within_section])

        # TODO - account for last_x_offset in both branches here.
        if section_index == 0:
            # Get the last section from the line above, and find where to move in it.
            target_row = line_index - 1
            target_column = self._wrapped_document.get_target_document_column(
                target_row, current_visual_offset, -1, tab_width
            )
            target_location = target_row, target_column
        else:
            # Stay on the same document line, but move backwards.
            # Since the section above could be shorter, we need to clamp the column
            # to a valid value.
            target_column = self._wrapped_document.get_target_document_column(
                line_index, current_visual_offset, section_index - 1, tab_width
            )
            target_location = line_index, target_column

        return target_location

    def get_location_below(self, location: Location, tab_width: int) -> Location:
        """Given a location in the raw document, return the raw document
        location corresponding to moving down in the wrapped representation
        of the document.

        Args:
            location: The location in the raw document.
            tab_width: The width of the tab stops.

        Returns:
            The location which is *visually* below the given location.
        """
        line_index, column_index = location
        document = self._document

        if self.is_last_document_line(location):
            return line_index, len(document[line_index])

        wrap_offsets = self._wrapped_document.get_offsets(line_index)
        section_start_columns = [0, *wrap_offsets]
        section_index = bisect(wrap_offsets, column_index)
        offset_within_section = column_index - section_start_columns[section_index]
        wrapped_line = self._wrapped_document.get_sections(line_index)
        section = wrapped_line[section_index]
        current_visual_offset = cell_len(section[:offset_within_section])

        # If we're at the last section/row of a wrapped line
        if section_index == len(wrapped_line) - 1:
            # Go to the first section of the line below.
            target_row = line_index + 1
            target_column = self._wrapped_document.get_target_document_column(
                target_row, current_visual_offset, 0, tab_width
            )
            target_location = target_row, target_column
        else:
            # Stay on the same document line, but move forwards to
            # the location on the section below with the same visual offset.
            target_column = self._wrapped_document.get_target_document_column(
                line_index, current_visual_offset, section_index + 1, tab_width
            )
            target_location = line_index, target_column

        return target_location

    def get_location_end(self, location: Location) -> Location:
        """Get the location corresponding to the end of the current section.

        Args:
            location: The current location.

        Returns:
            The location corresponding to the end of the wrapped line.
        """
        line_index, column_offset = location
        wrap_offsets = self._wrapped_document.get_offsets(line_index)
        if wrap_offsets:
            # Get the next wrap offset to the right
            next_offset_right = bisect(wrap_offsets, column_offset)
            # There's no more wrapping to the right of this location - go to line end.
            if next_offset_right == len(wrap_offsets):
                return line_index, len(self._document[line_index])
            # We've found a wrap point
            return line_index, wrap_offsets[next_offset_right] - 1
        else:
            # No wrapping to consider - go to the start/end of the document line.
            target_column = len(self._document[line_index])
            return line_index, target_column

    def get_location_home(self, location: Location) -> Location:
        """Get the location corresponding to the start of the current section."""
        line_index, column_offset = location
        wrap_offsets = self._wrapped_document.get_offsets(line_index)
        if wrap_offsets:
            next_offset_left = bisect(wrap_offsets, column_offset)
            if next_offset_left == 0:
                return line_index, 0
            return line_index, wrap_offsets[next_offset_left - 1]
        else:
            # No wrapping to consider, go to the start of the document line
            return line_index, 0

    # TODO - we need to implement methods for going page up and page down
    #  perhaps we just need a method:  given a location and a y-offset return
    #  the location corresponding to the y-offset applied to the location in the
    #  *wrapped* document.

    def clamp_reachable(self, location: Location) -> Location:
        """Given a location, return the nearest location that corresponds to a
        reachable location in the document.

        Args:
            location: A location.

        Returns:
            The nearest reachable location in the document.
        """
        document = self._document
        row, column = location
        clamped_row = clamp(row, 0, document.line_count - 1)

        row_text = self._document[clamped_row]
        clamped_column = clamp(column, 0, len(row_text))
        return clamped_row, clamped_column


def index(sequence: Sequence, value: Any) -> int:
    """Locate the leftmost item in the sequence equal to value via bisection.

    Args:
        sequence: The sequence to search in.
        value: The value to find.

    Returns:
        The index of the value, or -1 if the value is not found in the sequence.
    """
    insert_index = bisect_left(sequence, value)
    if insert_index != len(sequence) and sequence[insert_index] == value:
        return insert_index
    return -1
