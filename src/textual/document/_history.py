from __future__ import annotations

import time
from dataclasses import dataclass, field

from textual.widgets._text_area import Edit


@dataclass
class UndoStack:
    batch_window: float = 5.0
    """Number of seconds to batch edits within."""

    batches: list[list[Edit]] = field(init=False, default_factory=list)
    """Batching Edit operations together."""

    def record(self, edit: Edit) -> None:
        """Defines the rules for whether an Edit action should be included in
        a prior batch or added to a new batch."""
        current_time = time.monotonic()

        #
        if not self.batches:
            new_batch = [edit]
