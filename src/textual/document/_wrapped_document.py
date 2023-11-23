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
                target_line_index = line_index
                target_line_offsets = line_offsets
                break

            current_offset = next_offset
        else:
            # Offset doesn't match any line => land on bottom wrapped line
            target_line_index = -1
            target_line_offsets = self._wrap_offsets[target_line_index]
            wrapped_lines = Text(self.document[target_line_index]).divide(
                target_line_offsets
            )
            target_wrapped_section = wrapped_lines[-1].plain
            target_column_index = cell_width_to_column_index(
                target_wrapped_section, x, tab_width
            )
            target_column_index += sum(
                len(wrapped_section) for wrapped_section in wrapped_lines[:-1]
            )
            return len(self._wrap_offsets) - 1, target_column_index

        # We've found the relevant line, now find the character by
        # looking at the character corresponding to the offset width.
        wrapped_lines = Text(self.document[target_line_index]).divide(
            target_line_offsets
        )

        target_wrapped_section_index = y - current_offset
        # wrapped_section is the text that appears on a single y_offset within
        # the TextArea. It's a potentially wrapped portion of a larger line from
        # the original document.
        target_wrapped_section = wrapped_lines[target_wrapped_section_index].plain

        # Get the column index within this wrapped section of the line
        target_column_index = cell_width_to_column_index(
            target_wrapped_section, x, tab_width
        )

        # Add the offsets from the wrapped sections above this one (from the same raw document line)
        target_column_index += sum(
            len(wrapped_section)
            for wrapped_section in wrapped_lines[:target_wrapped_section_index]
        )

        return target_line_index, target_column_index

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
