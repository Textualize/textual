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


'''
### Approach
- Introduce a secondary coordinate system "wrapped coordinates". This is in addition to the existing "document coordinates".
- Moving the cursor in any way should be done in wrapped-coordinate-space.
- When the cursor moves in wrapped coordinate space, the document coordinate space selection should be updated accordingly.
	- So we need a mechanism to convert between wrapped coordinates and document coordinates.

Lets add wrapping and *then* extract the `CodeEditor` functionality.

- [x] Add `soft_wrap` boolean flag to TextArea.
- [ ] Display wrapped text
- [ ] Record cursor location in wrapped space
- [ ] Render the cursor based on the wrapped space instead of the document location
- [ ] When moving cursor, update location in wrapped space
- [ ] When the wrapped space location updates, update the document space location via watcher

---
### When are wrapped lines computed?
- When document is loaded, compute wrapped lines.
- When document is edited, re-compute and update all wrapped lines below the edited line.
- There are no other line wrapping computations performed.
### How do wrapped lines affect rendering?
- `render_line` will be indexing into the wrapped document, and displaying a view into that. This differs from the current approach, where it's a view 


### When and what to wrap:

- on document load: wrap whole document
- on edit: wrap affected line(s) - remember when we perform an edit, we are told the old start and new end locations, so we can find all the relevant lines which need to be re-wrapped. perform the re-wrapping of these lines, and insert the new lines into the corresponding position in the wrapped documents. TO SUPPORT THIS, our document view needs the ability to be informed about the lines impacted by an edit, and incrementally refresh the affected lines.

can we associate lines in the document with their wrapped counterparts?
```python
wrapped_lines: list[list[str]]
"""A mapping of line indices to the wrapped versions of those lines."""
```
we fill this cache when the document is loaded, only if wrapping is enabled.

when an edit occurs:
- delete the content on the lines between old_start and old_end
- take the new content and wrap it, ensuring we remember which document line each wrapped line corresponds to (use `list[list[str]]`)
	- we may need a function like `apply_edit(from_line, to_line)` which internally grabs the relevant lines from the source document and wraps them
- insert the newly wrapped content into wrapped_line_cache at old_start (ensuring it pushes down content below it, rather than replacing)
- ensure a refresh is triggered

**convert from document space to wrapped space**
(we need this to determine what should happen when we move the cursor, and where to render the cursor on screen)
- iterate over wrapped lines, summing up the lengths of all the wrapped lines to get to the document line.
- when we arrive at the line, take as many lines as possible from the value, then check how far into the final line we can go to arrive at the corresponding wrapped space location.
Note that we can also go from a document space line number and retrieve 

**convert from wrapped space to document space**
(to determine where in the document an insert should happen, since we insert into a position in document space)

---
there should be an efficient means of converting more than one location which prevents us from having to iterate through several lines for each location e.g.
`to_wrapped_space(*values: Location) -> tuple[Location]`
and similarly for the reverse direction!

---

'''
