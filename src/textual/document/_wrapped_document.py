"""A view into a Document which wraps the document at a certain
width and can be queried to retrieve lines from the *wrapped* version
of the document.

Allows for incremental updates, ensuring that we only re-wrap ranges of the document
that were influenced by edits.
"""
from __future__ import annotations

from rich._wrap import divide_line
from rich.text import Text

from textual.document._document import DocumentBase, Location


class WrappedDocument:
    def __init__(
        self,
        document: DocumentBase,
        width: int = 0,
    ) -> None:
        """Construct a WrappedDocumentView.

        Args:
            document: The document to wrap.
            width: The cell-width to wrap at.
        """
        self._document = document
        """The document wrapping is performed on."""

        self._width = width
        """The maximum cell-width per line."""

        self._wrap_offsets: list[list[int]] = []
        """Maps line indices to the offsets within the line wrapping
        breaks should be added."""

    def wrap_all(self) -> None:
        """Wrap and cache all lines in the document."""
        new_wrapped_lines = []
        append_wrapped_line = new_wrapped_lines.append
        width = self._width

        for line in self._document.lines:
            append_wrapped_line(divide_line(line, width))

        self._wrap_offsets = new_wrapped_lines

    @property
    def lines(self) -> list[list[str]]:
        """The lines of the wrapped version of the Document.

        Each index in the returned list represents a line index in the raw
        document. The list[str] at each index is the content of the raw document line
        split into multiple lines via wrapping.
        """
        wrapped_lines = []
        for line_index, line in enumerate(self._document.lines):
            divided = Text(line).divide(self._wrap_offsets[line_index])
            wrapped_lines.append([section.plain for section in divided])
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

        # Get the start and the end lines of the edit in document space
        start_row, _ = start
        end_row, _ = new_end

        # +1 since we go to the start of the next row, and +1 for inclusive.
        new_lines = self._document.lines[start_row : end_row + 2]

        new_wrap_offsets = []
        for line in new_lines:
            wrapped_line = divide_line(line, self._width)
            new_wrap_offsets.append(wrapped_line)

        # Replace the range start->old with the new wrapped lines
        old_end_row, _ = old_end
        self._wrap_offsets[start_row:old_end_row] = new_wrap_offsets
