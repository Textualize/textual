from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from textual.document._document import EditResult, Location, Selection

if TYPE_CHECKING:
    from textual.widgets import TextArea


@dataclass
class Edit:
    """Implements the Undoable protocol to replace text at some range within a document."""

    text: str
    """The text to insert. An empty string is equivalent to deletion."""

    from_location: Location
    """The start location of the insert."""

    to_location: Location
    """The end location of the insert"""

    _original_selection: Selection | None = field(init=False, default=None)
    """The Selection when the edit was originally performed, to be restored on undo."""

    _updated_selection: Selection | None = field(init=False, default=None)
    """Where the selection should move to after the replace happens."""

    _edit_result: EditResult | None = field(init=False, default=None)
    """The result of doing the edit."""

    def _update_location(self, location: Location, delete: Selection, insert: Selection, target: Location) -> Location:
        """Move a given location with respect to deletion and insertion ranges of an edit.

        Args:
            location: Location before the edit.
            delete: Range which is deleted during the edit.
            insert: Range which is inserted during the edit.
            target: Returned location when `location` is within the deletion range,
                typically the start or the end of the insertion range.

        Returns:
            Location after the edit.
        """
        loc_ = location
        del_ = delete
        ins_ = insert

        if loc_ < del_:
            # `loc_` is not affected by the edit and thus does not change
            pass
        elif loc_ in del_:
            # `loc_` is within the deletion range and set to the `target`
            loc_ = target
        elif loc_ > del_:
            # `loc_` is shifted by the difference in length
            # between delete and insert operations
            shift = (ins_.end[0] - del_.end[0], ins_.end[1] - del_.end[1])

            # only shift columns when edit happened in the same row `loc_` is also in
            if del_.end[0] < loc_[0]:
                shift = (shift[0], 0)

            loc_ = (loc_[0] + shift[0], loc_[1] + shift[1])

        return loc_


    def do(self, text_area: TextArea, record_selection: bool = True) -> EditResult:
        """Perform the edit operation.

        Args:
            text_area: The `TextArea` to perform the edit on.
            record_selection: If True, record the current selection in the TextArea
                so that it may be restored if this Edit is undone in the future.

        Returns:
            An `EditResult` containing information about the replace operation.
        """
        if record_selection:
            self._original_selection = text_area.selection

        edit_result = text_area.document.replace_range(self.top, self.bottom, self.text)

        # This code is mostly handling how we adjust TextArea.selection
        # when an edit is made to the document programmatically.
        # We want a user who is typing away to maintain their relative
        # position in the document even if an insert happens before
        # their cursor position.

        # use the original selection for proper history undo/redo operations
        start, end = self._original_selection

        delete = Selection(self.top, self.bottom)
        insert = Selection(self.top, edit_result.end_location)

        if (start in delete) and (end in delete):
            # the current selection has been deleted, i.e. is within the deletion range;
            # reset cursor to end of edit, i.e. insert range
            start, end = insert.end, insert.end
        else:
            # reverse target locations if the current selection is reversed
            if start > end:
                target_start, target_end = insert.start, insert.end
            else:
                target_start, target_end = insert.end, insert.start

            ## start
            # before edit - no-op
            # within edit - shift to end of edit
            #  after edit - shift by edit length

            ## end
            # before edit - no-op
            # within edit - shift to start of edit
            #  after edit - shift by edit length

            start = self._update_location(start, delete, insert, target_start)
            end = self._update_location(end, delete, insert, target_end)

        self._updated_selection = Selection(start, end)
        self._edit_result = edit_result

        return edit_result

    def undo(self, text_area: TextArea) -> EditResult:
        """Undo the edit operation.

        Looks at the data stored in the edit, and performs the inverse operation of `Edit.do`.

        Args:
            text_area: The `TextArea` to undo the insert operation on.

        Returns:
            An `EditResult` containing information about the replace operation.
        """
        replaced_text = self._edit_result.replaced_text
        edit_end = self._edit_result.end_location

        # Replace the span of the edit with the text that was originally there.
        undo_edit_result = text_area.document.replace_range(
            self.top, edit_end, replaced_text
        )
        self._updated_selection = self._original_selection

        return undo_edit_result

    def after(self, text_area: TextArea) -> None:
        """Hook for running code after an Edit has been performed via `Edit.do` *and*
        side effects such as re-wrapping the document and refreshing the display
        have completed.

        For example, we can't record cursor visual offset until we know where the cursor will
        land *after* wrapping has been performed, so we must wait until here to do it.

        Args:
            text_area: The `TextArea` this operation was performed on.
        """
        if self._updated_selection is not None:
            text_area.selection = self._updated_selection
        text_area.record_cursor_width()

    @property
    def top(self) -> Location:
        """The Location impacted by this edit that is nearest the start of the document."""
        return min([self.from_location, self.to_location])

    @property
    def bottom(self) -> Location:
        """The Location impacted by this edit that is nearest the end of the document."""
        return max([self.from_location, self.to_location])
