from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field

from textual.document._edit import Edit


class HistoryException(Exception):
    """Indicates misuse of the EditHistory API.

    For example, trying to undo() an Edit that has yet to be done.
    """


@dataclass
class EditHistory:
    """Manages batching/checkpointing of Edits into groups that can be undone/redone in the TextArea."""

    max_checkpoints: int

    checkpoint_timer: float
    """Maximum number of seconds since last edit until a new batch is created."""

    checkpoint_max_characters: int
    """Maximum number of characters that can appear in a batch before a new batch is formed."""

    _last_edit_time: float = field(init=False, default_factory=time.monotonic)

    _character_count: int = field(init=False, default=0)
    """Track number of characters replaced + inserted since last batch creation."""

    _force_end_batch: bool = field(init=False, default=False)
    """Flag to force the creation of a new batch for the next recorded edit."""

    _previously_replaced: bool = field(init=False, default=False)
    """Records whether the most recent edit was a replacement or a pure insertion.
    
    If an edit removes any text from the document at all, it's considered a replacement.
    Every other edit is considered a pure insertion.
    """

    def __post_init__(self) -> None:
        self._undo_stack: deque[list[Edit]] = deque(maxlen=self.max_checkpoints)
        """Batching Edit operations together (edits are simply grouped together in lists)."""
        self._redo_stack: deque[list[Edit]] = deque()
        """Stores batches that have been undone, allowing them to be redone."""

    def record(self, edit: Edit) -> None:
        """Record an Edit so that it may be undone and redone.

        Determines whether to batch the Edit with previous Edits, or create a new batch/checkpoint.

        This method must be called exactly once per edit, in chronological order.

        A new batch/checkpoint is created when:

        - The undo stack is empty.
        - The checkpoint timer expires.
        - The maximum number of characters permitted in a checkpoint is reached.
        - A redo is performed (we should not add new edits to a batch that has been redone).
        - The programmer has requested a new batch via a call to `force_new_batch`.
            - e.g. the TextArea widget may call this method in some circumstances.
            - Clicking to move the cursor elsewhere in the document should create a new batch.
            - Movement of the cursor via a keyboard action that is NOT an edit.
            - Blurring the TextArea creates a new checkpoint.
        - The current edit involves a deletion/replacement and the previous edit did not.
        - The current edit is a pure insertion and the previous edit was not.
        - The edit involves insertion or deletion of one or more newline characters.
        - An edit which inserts more than a single character (a paste) gets an isolated batch.

        Args:
            edit: The edit to record.
        """
        edit_result = edit._edit_result
        if edit_result is None:
            raise HistoryException(
                "Cannot add an edit to history before it has been performed using `Edit.do`."
            )

        if edit.text == "" and edit_result.replaced_text == "":
            return None

        is_replacement = bool(edit_result.replaced_text)
        undo_stack = self._undo_stack
        current_time = self._get_time()
        edit_characters = len(edit.text)
        contains_newline = "\n" in edit.text or "\n" in edit_result.replaced_text

        # Determine whether to create a new batch, or add to the latest batch.
        if (
            not undo_stack
            or self._force_end_batch
            or edit_characters > 1
            or contains_newline
            or is_replacement != self._previously_replaced
            or current_time - self._last_edit_time > self.checkpoint_timer
            or self._character_count + edit_characters > self.checkpoint_max_characters
        ):
            # Create a new batch (creating a "checkpoint").
            undo_stack.append([edit])
            self._character_count = edit_characters
            self._last_edit_time = current_time
            self._force_end_batch = False
        else:
            # Update the latest batch.
            undo_stack[-1].append(edit)
            self._character_count += edit_characters
            self._last_edit_time = current_time

        self._previously_replaced = is_replacement
        self._redo_stack.clear()

        # For some edits, we want to ensure the NEXT edit cannot be added to its batch,
        # so enforce a checkpoint now.
        if contains_newline or edit_characters > 1:
            self.checkpoint()

    def _pop_undo(self) -> list[Edit] | None:
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
        return None

    def _pop_redo(self) -> list[Edit] | None:
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
            self.checkpoint()
            return batch
        return None

    def clear(self) -> None:
        """Completely clear the history."""
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._last_edit_time = time.monotonic()
        self._force_end_batch = False
        self._previously_replaced = False

    def checkpoint(self) -> None:
        """Ensure the next recorded edit starts a new batch."""
        self._force_end_batch = True

    @property
    def undo_stack(self) -> list[list[Edit]]:
        """A copy of the undo stack, with references to the original Edits."""
        return list(self._undo_stack)

    @property
    def redo_stack(self) -> list[list[Edit]]:
        """A copy of the redo stack, with references to the original Edits."""
        return list(self._redo_stack)

    def _get_time(self) -> float:
        """Get the time from the monotonic clock.

        Returns:
            The result of `time.monotonic()` as a float.
        """
        return time.monotonic()
