from __future__ import annotations

import time
from dataclasses import dataclass, field

from textual.document._edit import Edit


class HistoryException(Exception):
    pass


@dataclass
class EditHistory:
    checkpoint_timer: float
    """Maximum number of seconds since last edit until a new batch is created."""

    checkpoint_max_characters: int
    """Maximum number of characters that can appear in a batch before a new batch is formed."""

    _undo_stack: list[list[Edit]] = field(init=False, default_factory=list)
    """Batching Edit operations together (edits are simply grouped together in lists)."""

    _redo_stack: list[list[Edit]] = field(init=False, default_factory=list)
    """Stores batches that have been undone, allowing them to be redone."""

    _last_edit_time: float = field(init=False, default_factory=time.monotonic)

    _character_count: int = field(init=False, default=0)
    """Track number of characters replaced + inserted since last batch creation."""

    _force_end_batch: bool = field(init=False, default=False)
    """Flag to force the creation of a new batch for the next recorded edit."""

    def record_edit(self, edit: Edit) -> None:
        """Record an Edit so that it may be undone and redone.

        Args:
            edit: The edit to record.
        """
        if edit._edit_result is None:
            raise HistoryException(
                "Cannot add an edit to history before it has been performed using `Edit.do`."
            )

        undo_stack = self._undo_stack
        current_time = time.monotonic()
        edit_characters = self._count_edit_characters(edit)

        # Determine whether to create a new batch, or add to the latest batch.
        if (
            not undo_stack
            or self._force_end_batch
            or current_time - self._last_edit_time > self.checkpoint_timer
            or self._character_count + edit_characters > self.checkpoint_max_characters
            or "\n" in edit.text
            or "\n" in edit._edit_result.replaced_text
        ):
            # Create a new batch (creating a "checkpoint").
            undo_stack.append([edit])
            self._character_count = edit_characters  # TODO - check this
            self._last_edit_time = current_time
            self._force_end_batch = False
        else:
            # Update the latest batch.
            undo_stack[-1].append(edit)
            self._character_count += edit_characters
            self._last_edit_time = current_time

        self._redo_stack.clear()

    def pop_undo(self) -> list[Edit] | None:
        """Pop the latest batch from the undo stack and return it.

        This will also place it on the redo stack.

        Returns:
            The batch of Edits from the top of the undo stack or None if it's empty.
        """
        undo_stack = self._undo_stack
        redo_stack = self._redo_stack
        if undo_stack:
            batch = undo_stack.pop()
            redo_stack.append(batch)
            return batch

    def pop_redo(self) -> list[Edit] | None:
        """Redo the latest batch on the redo stack and return it.

        This will also place it on the undo stack (with a forced checkpoint to ensure
        this undo does not get batched with other edits).

        Returns:
            The batch of Edits from the top of the redo stack or None if it's empty.
        """
        undo_stack = self._undo_stack
        redo_stack = self._redo_stack
        if redo_stack:
            batch = redo_stack.pop()
            undo_stack.append(batch)
            # Ensure edits which follow cannot be added to the redone batch.
            self.force_end_batch()
            return batch

    def reset(self) -> None:
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._last_edit_time = time.monotonic()
        self._force_end_batch = False

    def force_end_batch(self) -> None:
        """Ensure the next recorded edit starts a new batch."""
        self._force_end_batch = True

    def _count_edit_characters(self, edit: Edit) -> int:
        """Return the number of characters contained in an Edit.

        Args:
            edit: The edit to count characters in.

        Returns:
            The number of characters replaced + inserted in the Edit.
        """
        inserted_characters = len(edit.text)
        replaced_characters = len(edit._edit_result.replaced_text)
        return replaced_characters + inserted_characters
