"""Implements a progress bar widget."""

from __future__ import annotations

from math import ceil
from time import monotonic
from typing import Callable, Optional

from rich.style import Style

from textual.geometry import clamp

from ..app import ComposeResult, RenderResult
from ..containers import Horizontal
from ..reactive import reactive
from ..renderables.bar import Bar as BarRenderable
from ..timer import Timer
from ..widget import Widget
from ..widgets import Label


class Bar(Widget, can_focus=False):
    """The bar portion of the progress bar."""

    COMPONENT_CLASSES = {"bar--bar", "bar--complete", "bar--indeterminate"}
    """
    The bar sub-widget provides the component classes that follow.

    These component classes let you modify the foreground and background color of the
    bar in its different states.

    | Class | Description |
    | :- | :- |
    | `bar--bar` | Style of the bar (may be used to change the color). |
    | `bar--complete` | Style of the bar when it's complete. |
    | `bar--indeterminate` | Style of the bar when it's in an indeterminate state. |
    """

    DEFAULT_CSS = """
    Bar {
        width: 32;
        height: 1;
    }
    Bar > .bar--bar {
        color: $warning;
        background: $foreground 10%;
    }
    Bar > .bar--indeterminate {
        color: $error;
        background: $foreground 10%;
    }
    Bar > .bar--complete {
        color: $success;
        background: $foreground 10%;
    }
    """

    _percentage: reactive[float | None] = reactive[Optional[float]](None)
    """The percentage of progress that has been completed."""
    _start_time: float | None
    """The time when the widget started tracking progress."""

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        """Create a bar for a [`ProgressBar`][textual.widgets.ProgressBar]."""
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._start_time = None
        self._percentage = None

    def watch__percentage(self, percentage: float | None) -> None:
        """Manage the timer that enables the indeterminate bar animation."""
        if percentage is not None:
            self.auto_refresh = None
        else:
            self.auto_refresh = 1 / 15

    def render(self) -> RenderResult:
        """Render the bar with the correct portion filled."""
        if self._percentage is None:
            return self.render_indeterminate()
        else:
            bar_style = (
                self.get_component_rich_style("bar--bar")
                if self._percentage < 1
                else self.get_component_rich_style("bar--complete")
            )
            return BarRenderable(
                highlight_range=(0, self.size.width * self._percentage),
                highlight_style=Style.from_color(bar_style.color),
                background_style=Style.from_color(bar_style.bgcolor),
            )

    def render_indeterminate(self) -> RenderResult:
        """Render a frame of the indeterminate progress bar animation."""
        width = self.size.width
        highlighted_bar_width = 0.25 * width
        # Width used to enable the visual effect of the bar going into the corners.
        total_imaginary_width = width + highlighted_bar_width

        speed = 30  # Cells per second.
        # Compute the position of the bar.
        start = (speed * self._get_elapsed_time()) % (2 * total_imaginary_width)
        if start > total_imaginary_width:
            # If the bar is to the right of its width, wrap it back from right to left.
            start = 2 * total_imaginary_width - start  # = (tiw - (start - tiw))
        start -= highlighted_bar_width
        end = start + highlighted_bar_width

        bar_style = self.get_component_rich_style("bar--indeterminate")
        return BarRenderable(
            highlight_range=(max(0, start), min(end, width)),
            highlight_style=Style.from_color(bar_style.color),
            background_style=Style.from_color(bar_style.bgcolor),
        )

    def _get_elapsed_time(self) -> float:
        """Get time for the indeterminate progress animation.

        This method ensures that the progress bar animation always starts at the
        beginning and it also makes it easier to test the bar if we monkey patch
        this method.

        Returns:
            The time elapsed since the bar started being animated.
        """
        if self._start_time is None:
            self._start_time = monotonic()
            return 0
        return monotonic() - self._start_time


class PercentageStatus(Label):
    """A label to display the percentage status of the progress bar."""

    DEFAULT_CSS = """
    PercentageStatus {
        width: 5;
        content-align-horizontal: right;
    }
    """

    _label_text: reactive[str] = reactive("", repaint=False)
    """This is used as an auxiliary reactive to only refresh the label when needed."""
    _percentage: reactive[float | None] = reactive[Optional[float]](None)
    """The percentage of progress that has been completed."""

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._percentage = None
        self._label_text = "--%"

    def watch__percentage(self, percentage: float | None) -> None:
        """Manage the text that shows the percentage of progress."""
        if percentage is None:
            self._label_text = "--%"
        else:
            self._label_text = f"{int(100 * percentage)}%"

    def watch__label_text(self, label_text: str) -> None:
        """If the label text changed, update the renderable (which also refreshes)."""
        self.update(label_text)


class ETAStatus(Label):
    """A label to display the estimated time until completion of the progress bar."""

    DEFAULT_CSS = """
    ETAStatus {
        width: 9;
        content-align-horizontal: right;
    }
    """

    _label_text: reactive[str] = reactive("", repaint=False)
    """This is used as an auxiliary reactive to only refresh the label when needed."""
    _percentage: reactive[float | None] = reactive[Optional[float]](None)
    """The percentage of progress that has been completed."""
    _refresh_timer: Timer
    """Timer to update ETA status even when progress stalls."""
    _start_time: float | None
    """The time when the widget started tracking progress."""

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._percentage = None
        self._label_text = "--:--:--"
        self._start_time = None

    def on_mount(self) -> None:
        """Periodically refresh the countdown so that the ETA is always up to date."""
        self._refresh_timer = self.set_interval(1 / 2, self.update_eta, pause=True)

    def watch__percentage(self, percentage: float | None) -> None:
        if percentage is None:
            self._label_text = "--:--:--"
        else:
            self._refresh_timer.reset()
            self.update_eta()

    def update_eta(self) -> None:
        """Update the ETA display."""
        percentage = self._percentage
        delta = self._get_elapsed_time()
        # We display --:--:-- if we haven't started, if we are done,
        # or if we don't know when we started keeping track of time.
        if not percentage or percentage >= 1 or not delta:
            self._label_text = "--:--:--"
            # If we are done, we can delete the timer that periodically refreshes
            # the countdown display.
            if percentage is not None and percentage >= 1:
                self.auto_refresh = None
        # Render a countdown timer with hh:mm:ss, unless it's a LONG time.
        else:
            left = ceil((delta / percentage) * (1 - percentage))
            minutes, seconds = divmod(left, 60)
            hours, minutes = divmod(minutes, 60)
            if hours > 999999:
                self._label_text = "+999999h"
            elif hours > 99:
                self._label_text = f"{hours}h"
            else:
                self._label_text = f"{hours:02}:{minutes:02}:{seconds:02}"

    def _get_elapsed_time(self) -> float:
        """Get time to estimate time to progress completion.

        Returns:
            The time elapsed since the bar started being animated.
        """
        if self._start_time is None:
            self._start_time = monotonic()
            return 0
        return monotonic() - self._start_time

    def watch__label_text(self, label_text: str) -> None:
        """If the ETA label changed, update the renderable (which also refreshes)."""
        self.update(label_text)


class ProgressBar(Widget, can_focus=False):
    """A progress bar widget."""

    DEFAULT_CSS = """
    ProgressBar > Horizontal {
        width: auto;
        height: auto;
    }
    ProgressBar {
        width: auto;
        height: 1;
    }
    """

    progress: reactive[float] = reactive(0.0)
    """The progress so far, in number of steps."""
    total: reactive[float | None] = reactive[Optional[float]](None)
    """The total number of steps associated with this progress bar, when known.

    The value `None` will render an indeterminate progress bar.
    Once `total` is set to a numerical value, it cannot be set back to `None`.
    """
    percentage: reactive[float | None] = reactive[Optional[float]](None)
    """The percentage of progress that has been completed.

    The percentage is a value between 0 and 1 and the returned value is only
    `None` if the total progress of the bar hasn't been set yet.
    In other words, after the progress bar emits the message
    [`ProgressBar.Started`][textual.widgets.ProgressBar.Started],
    the value of `percentage` is always not `None`.

    Example:
        ```py
        progress_bar = ProgressBar()
        print(progress_bar.percentage)  # None
        progress_bar.update(total=100)
        progress_bar.advance(50)
        print(progress_bar.percentage)  # 0.5
        ```
    """

    def __init__(
        self,
        total: float | None = None,
        *,
        show_bar: bool = True,
        show_percentage: bool = True,
        show_eta: bool = True,
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
                    yield ProgressBar(total=100)

                def key_space(self):
                    self.query_one(ProgressBar).advance(5)
            ```

        Args:
            total: The total number of steps in the progress if known.
            show_bar: Whether to show the bar portion of the progress bar.
            show_percentage: Whether to show the percentage status of the bar.
            show_eta: Whether to show the ETA countdown of the progress bar.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.show_bar = show_bar
        self.show_percentage = show_percentage
        self.show_eta = show_eta

        self.total = total

    def compose(self) -> ComposeResult:
        # We create a closure so that we can determine what are the sub-widgets
        # that are present and, therefore, will need to be notified about changes
        # to the percentage.
        def update_percentage(widget: Widget) -> Callable[[float | None], None]:
            """Closure to allow updating the percentage of a given widget."""

            def updater(percentage: float | None) -> None:
                """Update the percentage reactive of the enclosed widget."""
                widget._percentage = percentage

            return updater

        with Horizontal():
            if self.show_bar:
                bar = Bar(id="bar")
                self.watch(self, "percentage", update_percentage(bar))
                yield bar
            if self.show_percentage:
                percentage_status = PercentageStatus(id="percentage")
                self.watch(self, "percentage", update_percentage(percentage_status))
                yield percentage_status
            if self.show_eta:
                eta_status = ETAStatus(id="eta")
                self.watch(self, "percentage", update_percentage(eta_status))
                yield eta_status

    def validate_progress(self, progress: float) -> float:
        """Clamp the progress between 0 and the maximum total."""
        if self.total is not None:
            return clamp(progress, 0, self.total)
        return progress

    def validate_total(self, total: float | None) -> float | None:
        """Ensure the total is not negative."""
        if total is None:
            return total
        return max(0, total)

    def watch_total(self, total: float | None) -> None:
        """Re-validate progress."""
        self.progress = self.progress

    def compute_percentage(self) -> float | None:
        """Keep the percentage of progress updated automatically.

        This will report a percentage of `1` if the total is zero.
        """
        if self.total:
            return self.progress / self.total
        elif self.total == 0:
            return 1
        return None

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
