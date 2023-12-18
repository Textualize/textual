"""A view into a Document which wraps the document at a certain
width and can be queried to retrieve lines from the *wrapped* version
of the document.

Allows for incremental updates, ensuring that we only re-wrap ranges of the document
that were influenced by edits.
"""
from __future__ import annotations

from collections import defaultdict

from rich._wrap import divide_line
from rich.text import Text

from textual._cells import cell_width_to_column_index
from textual.document._document import DocumentBase, Location
from textual.geometry import Offset

VerticalOffset = int
LineIndex = int
SectionOffset = int


class WrappedDocument:
    def __init__(
        self,
        document: DocumentBase,
    ) -> None:
        """Construct a WrappedDocument.

        By default, a WrappedDocument is wrapped with width=0 (no wrapping).
        To wrap the document, use the wrap() method.

        Args:
            document: The document to wrap.
        """
        self.document = document
        """The document wrapping is performed on."""

        self._wrap_offsets: list[list[int]] = []
        """Maps line indices to the offsets within the line where wrapping
        breaks should be added."""

        self._offset_to_line_info: dict[
            VerticalOffset, tuple[LineIndex, SectionOffset]
        ] = {}
        """Maps y_offsets (from the top of the document) to line_index and the offset
        of the section within the line."""

        self._line_index_to_offsets: dict[
            LineIndex, list[VerticalOffset]
        ] = defaultdict(list)
        """Maps line indices to all the vertical offsets which correspond to that line."""

        # self._offset_to_section_offset: dict[int, int] = {}
        # """Maps y_offsets to the offsets of the section within the line."""

        self._width: int = 0
        """The width the document is currently wrapped at. This will correspond with
        the value last passed into the `wrap` method."""

        self.wrap(self._width)

    def wrap(self, width: int) -> None:
        """Wrap and cache all lines in the document.

        Args:
            width: The width to wrap at. 0 for no wrapping.
        """
        self._width = width

        # We're starting wrapping from scratch, so use fresh
        new_wrap_offsets = []
        offset_to_line_info = {}
        line_index_to_offsets: dict[LineIndex, list[VerticalOffset]] = defaultdict(list)

        append_wrap_offset = new_wrap_offsets.append
        current_offset = 0

        for line_index, line in enumerate(self.document.lines):
            wrap_offsets = divide_line(line, width) if width else []
            append_wrap_offset(wrap_offsets)
            for section_y_offset in range(len(wrap_offsets) + 1):
                offset_to_line_info[current_offset] = (line_index, section_y_offset)
                line_index_to_offsets[line_index].append(current_offset)
                current_offset += 1

        self._offset_to_line_info = offset_to_line_info
        self._line_index_to_offsets = line_index_to_offsets
        self._wrap_offsets = new_wrap_offsets
        print(f"BUILT offset_to_line_info = \n{offset_to_line_info!r}")
        print(f"BUILT line_index_to_offsets = \n{line_index_to_offsets!r}")

    @property
    def lines(self) -> list[list[str]]:
        """The lines of the wrapped version of the Document.

        Each index in the returned list represents a line index in the raw
        document. The list[str] at each index is the content of the raw document line
        split into multiple lines via wrapping.

        Returns:
            A list of lines from the wrapped version of the document.
        """
        wrapped_lines = []
        append = wrapped_lines.append
        for line_index, line in enumerate(self.document.lines):
            divided = Text(line).divide(self._wrap_offsets[line_index])
            append([section.plain for section in divided])

        return wrapped_lines

    @property
    def height(self) -> int:
        """The height of the wrapped document."""
        return sum(len(offsets) + 1 for offsets in self._wrap_offsets)

    def wrap_range(
        self,
        start: Location,
        old_end: Location,
        new_end: Location,
    ) -> None:
        """Incrementally recompute wrapping based on a performed edit.

        This must be called *after* the source document has been edited.

        Args:
            start: The start location of the edit that was performed in document-space.
            old_end: The old end location of the edit in document-space.
            new_end: The new end location of the edit in document-space.
        """

        # Get all the text on the lines between start and end in document space
        start_line_index, _ = start
        old_end_line_index, _ = old_end
        new_end_line_index, _ = new_end

        # Can we only rewrap a section of the line starting at the wrap point
        # to the left of the edit? There may be something we can do here. However,
        # an edit can alter wrap points before it.

        # Clearing old cached data
        current_offset = self._line_index_to_offsets.get(start_line_index)[0]

        print("Wrap--")
        print(
            f"ranges = start = {start_line_index!r}, old_end = {old_end!r}, new_end = {new_end!r}"
        )
        for line_index in range(start_line_index, old_end_line_index + 1):
            offsets = self._line_index_to_offsets.get(line_index)
            print(f"offsets for this range (will be deleted) = {offsets!r}")
            print(f"offset to line info contains = {self._offset_to_line_info!r}")
            for offset in offsets:
                del self._offset_to_line_info[offset]
            del self._line_index_to_offsets[line_index]

        new_lines = self.document.lines[start_line_index : new_end_line_index + 1]
        print(f"new lines for range = {new_lines!r}")

        new_wrap_offsets = []
        append_wrap_offset = new_wrap_offsets.append
        width = self._width

        # Add the new offsets between start and new end (the new post-edit offsets)
        for line_index, line in enumerate(new_lines, start_line_index):
            wrap_offsets = divide_line(line, width) if width else []
            append_wrap_offset(wrap_offsets)
            for section_offset in range(len(wrap_offsets) + 1):
                self._line_index_to_offsets[line_index].append(current_offset)
                self._offset_to_line_info[current_offset] = (line_index, section_offset)
                current_offset += 1

        # Replace the range start -> old with the new wrapped lines
        print(f"after update, new wrap offsets = \n{new_wrap_offsets!r}")
        print(f"length of offsets before = {len(self._wrap_offsets)}")
        self._wrap_offsets[start_line_index : old_end_line_index + 1] = new_wrap_offsets
        print(f"length of offsets after = {len(self._wrap_offsets)}")

    def offset_to_location(self, offset: Offset, tab_width: int) -> Location:
        """Given an offset within the wrapped/visual display of the document,
        return the corresponding location in the document.

        Args:
            offset: The y-offset within the document.
            tab_width: The maximum width of tab characters in the document.

        Raises:
            ValueError: When the given offset does not correspond to a line
                in the document.

        Returns:
            The Location in the document corresponding to the given offset.
        """
        x, y = offset
        if x < 0 or y < 0:
            raise ValueError("Offset must be non-negative.")

        if not self._width:
            # No wrapping, so we directly map offset to location and clamp.
            line_index = min(y, len(self._wrap_offsets) - 1)
            column_index = min(x, len(self.document.get_line(line_index)))
            return line_index, column_index

        # Find the line corresponding to the given y offset in the wrapped document.
        get_target_document_column = self.get_target_document_column
        offset_data = self._offset_to_line_info.get(y)
        if offset_data is not None:
            line_index, section_y = offset_data
            location = line_index, get_target_document_column(
                line_index,
                x,
                section_y,
                tab_width,
            )
        else:
            location = len(self._wrap_offsets) - 1, get_target_document_column(
                -1, x, -1, tab_width
            )

        # Offset doesn't match any line => land on bottom wrapped line
        return location

    def get_target_document_column(
        self,
        line_index: int,
        x_offset: int,
        y_offset: int,
        tab_width: int,
    ) -> int:
        """Given a line index and the offsets within the wrapped version of that
        line, return the corresponding column index in the raw document.

        Args:
             line_index: The index of the line in the document.
             x_offset: The x-offset within the wrapped line.
             y_offset: The y-offset within the wrapped line (supports negative indexing).
             tab_width: The size of the tab stop.

        Returns:
            The column index corresponding to the line index and y offset.
        """

        # We've found the relevant line, now find the character by
        # looking at the character corresponding to the offset width.
        sections = self.get_sections(line_index)

        # wrapped_section is the text that appears on a single y_offset within
        # the TextArea. It's a potentially wrapped portion of a larger line from
        # the original document.
        target_section = sections[y_offset]

        # Add the offsets from the wrapped sections above this one (from the same raw document line)
        target_section_start = sum(
            len(wrapped_section) for wrapped_section in sections[:y_offset]
        )

        # Get the column index within this wrapped section of the line
        target_column_index = target_section_start + cell_width_to_column_index(
            target_section, x_offset, tab_width
        )

        # If we're on the final section of a line, the cursor can legally rest beyond the end by a single cell.
        # Otherwise, we'll need to ensure that we're keeping the cursor within the bounds of the target section.
        if y_offset != len(sections) - 1 and y_offset != -1:
            target_column_index = min(
                target_column_index, target_section_start + len(target_section) - 1
            )

        return target_column_index

    def get_sections(self, line_index: int) -> list[str]:
        line_offsets = self._wrap_offsets[line_index]
        wrapped_lines = Text(self.document[line_index]).divide(line_offsets)
        return [line.plain for line in wrapped_lines]

    def get_offsets(self, line_index: int) -> list[int]:
        """Given a line index, get the offsets within that line where wrapping
        should occur for the current document.

        Args:
            line_index: The index of the line within the document.

        Raises:
            ValueError: When `line_index` is out of bounds.

        Returns:
            The offsets within the line where wrapping should occur.
        """
        wrap_offsets = self._wrap_offsets
        out_of_bounds = line_index < 0 or line_index >= len(wrap_offsets)
        if out_of_bounds:
            raise ValueError(
                f"The document line index {line_index!r} is out of bounds. "
                f"The document contains {len(wrap_offsets)!r} lines."
            )
        return wrap_offsets[line_index]
