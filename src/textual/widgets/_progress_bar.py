"""Implements a progress bar widget."""

from __future__ import annotations

from rich.progress import Progress, TaskID

from textual.app import RenderResult
from textual.reactive import reactive
from textual.widget import Widget


class ProgressBar(Widget, can_focus=False):
    """A progress bar widget.

    This widget builds on top of [rich's Progress][rich.progress.Progress].
    """

    DEFAULT_CSS = """
    ProgressBar {
        height: 1;
    }
    """

    progress: reactive[float] = reactive(0.0)
    """The progress so far of the progress bar."""

    _progress: Progress
    """The reference to the [rich Progress object][rich.progress.Progress]."""
    _task_id: TaskID
    """The task ID for the progress bar task."""

    def __init__(
        self,
        total: float | None = 100,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        """Create a Progress Bar widget.

        Example:
            ```py
            class MyApp(App):
                def compose(self):
                    yield ProgressBar()

                def key_space(self):
                    self.query_one(ProgressBar).advance()
            ```

        Args:
            total: The total number of steps in the progress if known.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        # Skip the text column with the task label:
        self._progress = Progress(*Progress.get_default_columns()[1:])
        self._task_id = self._progress.add_task("_default_task", total=total)

    def watch_progress(self, progress: float) -> None:
        """Update the inner state of the progress bar when `progress` changes."""
        self._progress.update(self._task_id, completed=progress)

    def advance(self, advance: float = 1) -> None:
        """Advance the progress of the progress bar by the given amount."""
        self.progress += advance

    def render(self) -> RenderResult:
        """Render the progress bar."""
        return self._progress
