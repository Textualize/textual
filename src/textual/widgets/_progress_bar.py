"""Implements a progress bar widget."""

from __future__ import annotations

from math import ceil
from time import monotonic
from typing import Optional

from rich.style import Style

from textual.timer import Timer

from ..app import ComposeResult, RenderResult
from ..containers import Horizontal
from ..reactive import reactive
from ..renderables.bar import RenderableBar
from ..widget import Widget
from ..widgets import Label


class Bar(Widget, can_focus=False):
    """The bar portion of the progress bar."""

    COMPONENT_CLASSES = {"bar--bar", "bar--complete", "bar--indeterminate"}
    """
    | Class | Description |
    | :- | :- |
    | `bar--bar` | Style of the bar (may be used to change the color). |
    | `bar--complete` | Style of the bar when it's complete. |
    | `bar--indeterminate` | Style of the bar when it's in an indeterminate state. |
    """

    DEFAULT_CSS = """
    Bar {
        width: 1fr;
        height: 1;
    }
    Bar > .bar--bar, Bar > .bar--indeterminate {
        background: $foreground 10%;
        color: $warning;
    }
    Bar > .bar--complete {
        background: $foreground 10%;
        color: $success;
    }
    """

    _completion_percentage: reactive[float | None] = reactive[Optional[float]](None)
    """The percentage of the bar that should be filled or `None` if indeterminate.

    If the completion percentage is `None`, then the bar will render as
    an indeterminate progress bar.
    """
    _refresh_timer: Timer | None
    """Internal timer used to render the bar when it's in the indeterminate state."""

    def watch__completion_percentage(self, percentage: float | None) -> None:
        if percentage is not None:
            if self._refresh_timer:
                self._refresh_timer.stop()
                self._refresh_timer = None

        else:
            self._refresh_timer = self.set_interval(1 / 60, self.refresh)

    def render(self) -> RenderResult:
        if self._completion_percentage is None:
            return self.render_indeterminate()
        else:
            width = self.size.width
            bar_style = (
                self.get_component_rich_style("bar--bar")
                if self._completion_percentage < 1
                else self.get_component_rich_style("bar--complete")
            )
            return RenderableBar(
                highlight_range=(0, width * self._completion_percentage),
                highlight_style=Style.from_color(bar_style.color),
                background_style=Style.from_color(bar_style.bgcolor),
            )

    def render_indeterminate(self) -> RenderResult:
        width = self.size.width
        highlighted_bar_width = 0.25 * width
        total_imaginary_width = width + highlighted_bar_width

        speed = 30  # Cells per second.
        start = (speed * monotonic()) % (2 * total_imaginary_width)
        if start > total_imaginary_width:
            start = 2 * total_imaginary_width - start
        start -= highlighted_bar_width
        end = start + highlighted_bar_width

        bar_style = self.get_component_rich_style("bar--indeterminate")
        return RenderableBar(
            highlight_range=(max(0, start), min(end, width)),
            highlight_style=Style.from_color(bar_style.color),
            background_style=Style.from_color(bar_style.bgcolor),
        )


class PercentageStatus(Label):
    """A label to display the percentage status of the progress bar."""

    _completion_percentage: reactive[float | None] = reactive[Optional[float]](None)
    """The percentage of progress that has been completed or `None` if indeterminate."""

    DEFAULT_CSS = """
    PercentageStatus {
        width: 5;
        content-align-horizontal: right;
    }
    """

    def watch__completion_percentage(self, percentage: float | None) -> None:
        if percentage is None:
            self.renderable = "--%"
        else:
            self.renderable = f"{int(100 * percentage)}%"


class ETAStatus(Label):
    """A label to display the estimated time until completion of the progress bar."""

    _completion_percentage: reactive[float | None] = reactive[Optional[float]](None)
    """The percentage of progress that has been completed or `None` if indeterminate."""

    DEFAULT_CSS = """
    ETAStatus {
        width: 9;
        content-align-horizontal: right;
    }
    """

    _refresh_timer: Timer | None = None
    """Timer to update ETA status even when progress stalls."""
    _start_time: float | None = None
    """The time at which the progress started being tracked."""

    def watch__completion_percentage(self, percentage: float | None) -> None:
        if percentage is None:
            self.renderable = "--:--:--"
        else:
            if self._start_time is None:
                self._start_time = monotonic()

            if self._refresh_timer is None:
                self._refresh_timer = self.set_interval(1 / 2, self.update_eta)

            self._refresh_timer.reset()
            self.update_eta()

    def update_eta(self) -> None:
        """Update the ETA display."""
        percentage = self._completion_percentage
        if not percentage or percentage >= 1 or self._start_time is None:
            self.renderable = "--:--:--"
            if (
                percentage is not None
                and percentage >= 1
                and self._refresh_timer is not None
            ):
                self._refresh_timer.stop()
                self._refresh_timer = None
        else:
            delta = monotonic() - self._start_time
            left = ceil((delta / percentage) * (1 - percentage))
            minutes, seconds = divmod(left, 60)
            hours, minutes = divmod(minutes, 60)
            if hours > 999999:
                self.renderable = "+999999h"
            elif hours > 99:
                self.renderable = f"{hours}h"
            else:
                self.renderable = f"{hours:02}:{minutes:02}:{seconds:02}"
        self.refresh()


class ProgressBar(Widget, can_focus=False):
    """A progress bar widget."""

    DEFAULT_CSS = """
    Horizontal {
        width: auto;
        height: auto;
    }
    ProgressBar {
        height: 1;
    }
    """

    progress: reactive[float] = reactive(0.0)
    """The progress so far, in number of steps."""
    total: reactive[float | None] = reactive[Optional[float]](100.0)
    """The total number of steps associated with this progress bar, when known.

    The value `None` will render an indeterminate progress bar.
    Once `total` is set to a numerical value, it cannot be set back to `None`
    """
    percentage: reactive[float | None] = reactive[Optional[float]](None)
    """The percentage of progress that has been completed."""

    def __init__(
        self,
        total: float | None = 100,
        *,
        hide_bar: bool = False,
        hide_percentage: bool = False,
        hide_eta: bool = False,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        """Create a Progress Bar widget.

        The progress bar uses "steps" as the measurement unit.

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
            hide_bar: Whether to hide the bar portion from the progress bar.
            hide_percentage: Whether to hide the percentage status from the bar.
            hide_eta: Whether to hide the ETA countdown from the progress bar.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._bar = Bar()
        self._percentage_status = PercentageStatus()
        self._eta_status = ETAStatus()
        self.hide_bar = hide_bar
        self.hide_percentage = hide_percentage
        self.hide_eta = hide_eta

        self.percentage = None  # Without this, assigning self.total breaks. 🤔
        self.total = total

    def compose(self) -> ComposeResult:
        with Horizontal():
            if not self.hide_bar:
                yield self._bar
            if not self.hide_percentage:
                yield self._percentage_status
            if not self.hide_eta:
                yield self._eta_status

    def validate_progress(self, progress: float) -> float:
        if self.total is not None:
            return min(progress, self.total)
        return progress

    def compute_percentage(self) -> float | None:
        if self.total is not None:
            return self.progress / self.total
        return None

    def watch_percentage(self, percentage: float | None) -> None:
        self._bar._completion_percentage = percentage
        self._percentage_status._completion_percentage = percentage
        self._eta_status._completion_percentage = percentage

    def advance(self, advance: float = 1) -> None:
        """Advance the progress of the progress bar by the given amount.

        Example:
            ```py
            progress_bar.advance(10)  # Advance 10 steps.
            ```
        Args:
            advance: Number of steps to advance progress by.
        """
        self.progress += advance

    def update(
        self,
        *,
        total: float | None = None,
        progress: float | None = None,
        advance: float | None = None,
    ) -> None:
        """Update the progress bar with the given options.

        Options only affect the progress bar if they are not `None`.

        Example:
            ```py
            progress_bar.update(
                total=200,  # Set new total to 200 steps.
                progress=None,  # This has no effect.
            )
            ```

        Args:
            total: New total number of steps (if not `None`).
            progress: Set the progress to the given number of steps (if not `None`).
            advance: Advance the progress by this number of steps (if not `None`).
        """
        if total is not None:
            self.total = total
        if progress is not None:
            self.progress = progress
        if advance is not None:
            self.progress += advance
