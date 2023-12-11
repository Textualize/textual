"""A view into a Document which wraps the document at a certain
width and can be queried to retrieve lines from the *wrapped* version
of the document.

Allows for incremental updates, ensuring that we only re-wrap ranges of the document
that were influenced by edits.
"""
from __future__ import annotations

from rich._wrap import divide_line
from rich.text import Text

from textual._cells import cell_width_to_column_index
from textual.document._document import DocumentBase, Location
from textual.geometry import Offset


class WrappedDocument:
    def __init__(
        self,
        document: DocumentBase,
        width: int = 0,
    ) -> None:
        """Construct a WrappedDocument.

        Args:
            document: The document to wrap.
            width: The cell-width to wrap at. 0 for no wrapping.
        """
        self.document = document
        """The document wrapping is performed on."""

        self._width = width
        """The maximum cell-width per line."""

        self._wrap_offsets: list[list[int]] = []
        """Maps line indices to the offsets within the line where wrapping
        breaks should be added."""

        self._offset_to_document_line: list[int] = []
        """Allows us to quickly go from a y-offset within the wrapped document
        to the index of the line in the raw document."""

    def wrap(self) -> None:
        """Wrap and cache all lines in the document."""
        new_wrap_offsets = []
        append_wrap_offset = new_wrap_offsets.append
        width = self._width

        for line in self.document.lines:
            wrap_offsets = divide_line(line, width) if width else []
            append_wrap_offset(wrap_offsets)

        self._wrap_offsets = new_wrap_offsets

    @property
    def lines(self) -> list[list[str]]:
        """The lines of the wrapped version of the Document.

        Each index in the returned list represents a line index in the raw
        document. The list[str] at each index is the content of the raw document line
        split into multiple lines via wrapping.
        """
        wrapped_lines = []
        append = wrapped_lines.append
        for line_index, line in enumerate(self.document.lines):
            divided = Text(line).divide(self._wrap_offsets[line_index])
            append([section.plain for section in divided])
        return wrapped_lines

    def refresh_range(
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
        start_row, _ = start
        end_row, _ = new_end

        # +1 since we go to the start of the next row, and +1 for inclusive.
        new_lines = self.document.lines[start_row : end_row + 2]

        new_wrap_offsets = []
        append_wrap_offset = new_wrap_offsets.append
        width = self._width
        for line_index, line in enumerate(new_lines, start_row):
            wrap_offsets = divide_line(line, width) if width else []
            append_wrap_offset(wrap_offsets)

        # Replace the range start -> old with the new wrapped lines
        old_end_row, _ = old_end
        self._wrap_offsets[start_row:old_end_row] = new_wrap_offsets

    def offset_to_location(self, offset: Offset, tab_width: int) -> Location:
        """Given an offset within the wrapped/visual display of the document,
        return the corresponding line index.

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
            raise ValueError("Offset must be positive.")

        if not self._width:
            # No wrapping, so we directly map offset to location and clamp.
            row_index = min(y, len(self._wrap_offsets) - 1)
            column_index = min(x, len(self.document.get_line(row_index)))
            return row_index, column_index

        # Find the line corresponding to the given y offset in the wrapped document.
        current_offset = 0
        for line_index, line_offsets in enumerate(self._wrap_offsets):
            next_offset = current_offset + len(line_offsets) + 1
            if next_offset > y:
                # We've found the vertical offset.
                return line_index, self.get_target_document_column(
                    line_index, x, y - current_offset, tab_width
                )
            current_offset = next_offset

        # Offset doesn't match any line => land on bottom wrapped line
        return len(self._wrap_offsets) - 1, self.get_target_document_column(
            -1, x, -1, tab_width
        )

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
