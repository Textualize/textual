"""A view into a Document which wraps the document at a certain
width and can be queried to retrieve lines from the *wrapped* version
of the document."""
from __future__ import annotations

from rich.cells import chop_cells

from textual.document._document import Document, Location


class WrappedDocumentView:
    def __init__(
        self,
        document: Document,
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

        self._wrapped_lines: list[list[str]] = []
        """Cached wrapped document lines."""

        self._wrap_all()

        self._last_edit_count = document.edit_count
        """The edit_count of the document last time we wrapped.
        
        If the edit_count has not changed since we last performed
        wrapping, we can rely on any cached data since we know the
        document must be identical.
        """

    def _wrap_all(self) -> None:
        """Wrap and cache all lines in the document."""
        new_wrapped_lines = []
        append_wrapped_line = new_wrapped_lines.append
        width = self._width

        for line in self._document.lines:
            append_wrapped_line(chop_cells(line, width))

        self._wrapped_lines = new_wrapped_lines

    def refresh_range(
        self,
        start: Location,
        old_end: Location,
        new_end: Location,
    ) -> None:
        """Incrementally recompute wrapping based on a performed edit.

        Args:
            start: The start location of the edit that was performed in document-space.
            old_end: The old end location of the edit in document-space.
            new_end: The new end location of the edit in document-space.
        """


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
