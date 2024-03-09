"""Implements a progress bar widget."""

from __future__ import annotations

from math import ceil
from time import monotonic
from typing import Callable, Optional

from rich.style import Style

from .._types import UnusedParameter
from ..app import ComposeResult, RenderResult
from ..eta import ETA
from ..geometry import clamp
from ..reactive import reactive
from ..renderables.bar import Bar as BarRenderable
from ..widget import Widget
from ..widgets import Label

UNUSED = UnusedParameter()
"""Sentinel for method signatures."""


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

        &> .bar--bar {
            color: $warning;
            background: $foreground 10%;
        }
        &> .bar--indeterminate {
            color: $error;
            background: $foreground 10%;
        }
        &> .bar--complete {
            color: $success;
            background: $foreground 10%;
        }
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
        _get_time: Callable[[], float] = monotonic,
    ):
        """Create a bar for a [`ProgressBar`][textual.widgets.ProgressBar]."""
        self._get_time = _get_time
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._start_time = None
        self._percentage = None

    def watch__percentage(self, percentage: float | None) -> None:
        """Manage the timer that enables the indeterminate bar animation."""
        if percentage is not None:
            self.auto_refresh = None
        else:
            self.auto_refresh = 1 / 5

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

        start: float
        end: float
        if self.app.animation_level == "none":
            start = 0
            end = width
        else:
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
            self._start_time = self._get_time()
            return 0
        return self._get_time() - self._start_time


class PercentageStatus(Label):
    """A label to display the percentage status of the progress bar."""

    DEFAULT_CSS = """
    PercentageStatus {
        width: 5;
        content-align-horizontal: right;
    }
    """

    _percentage: reactive[float | None] = reactive[Optional[float]](None)
    """The percentage of progress that has been completed."""

    def render(self) -> RenderResult:
        percentage = self._percentage
        return "--%" if percentage is None else f"{int(100 * percentage)}%"


class ETAStatus(Label):
    """A label to display the estimated time until completion of the progress bar."""

    DEFAULT_CSS = """
    ETAStatus {
        width: 9;
        content-align-horizontal: right;
    }
    """
    eta: reactive[float | None] = reactive[Optional[float]](None)
    """Estimated number of seconds till completion."""

    def render(self) -> RenderResult:
        """Render the ETA display."""
        eta = self.eta
        if eta is None:
            return "--:--:--"
        else:
            minutes, seconds = divmod(ceil(eta), 60)
            hours, minutes = divmod(minutes, 60)
            if hours > 999999:
                return "+999999h"
            elif hours > 99:
                return f"{hours}h"
            else:
                return f"{hours:02}:{minutes:02}:{seconds:02}"


class ProgressBar(Widget, can_focus=False):
    """A progress bar widget."""

    DEFAULT_CSS = """
    ProgressBar {
        width: auto;
        height: 1;
        layout: horizontal;
    }
    """

    progress: reactive[float] = reactive(0.0)
    """The progress so far, in number of steps."""
    total: reactive[float | None] = reactive[Optional[float]](None)
    """The total number of steps associated with this progress bar, when known.

    The value `None` will render an indeterminate progress bar.
    """
    percentage: reactive[float | None] = reactive[Optional[float]](None)
    """The percentage of progress that has been completed.

    The percentage is a value between 0 and 1 and the returned value is only
    `None` if the total progress of the bar hasn't been set yet.

    Example:
        ```py
        progress_bar = ProgressBar()
        print(progress_bar.percentage)  # None
        progress_bar.update(total=100)
        progress_bar.advance(50)
        print(progress_bar.percentage)  # 0.5
        ```
    """
    _display_eta: reactive[int | None] = reactive[Optional[int]](None)

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
        _get_time: Callable[[], float] = monotonic,
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
        self.total = total
        self.show_bar = show_bar
        self.show_percentage = show_percentage
        self.show_eta = show_eta
        self._get_time = _get_time
        self._eta = ETA(_get_time=_get_time)

    def on_mount(self) -> None:
        self.update()
        self.set_interval(0.5, self.update)

    def compose(self) -> ComposeResult:
        if self.show_bar:
            yield Bar(id="bar", _get_time=self._get_time).data_bind(
                _percentage=ProgressBar.percentage
            )
        if self.show_percentage:
            yield PercentageStatus(id="percentage").data_bind(
                _percentage=ProgressBar.percentage
            )
        if self.show_eta:
            yield ETAStatus(id="eta").data_bind(eta=ProgressBar._display_eta)

    def _validate_progress(self, progress: float) -> float:
        """Clamp the progress between 0 and the maximum total."""
        if self.total is not None:
            return clamp(progress, 0, self.total)
        return progress

    def _validate_total(self, total: float | None) -> float | None:
        """Ensure the total is not negative."""
        if total is None:
            return total
        return max(0, total)

    def _compute_percentage(self) -> float | None:
        """Keep the percentage of progress updated automatically.

        This will report a percentage of `1` if the total is zero.
        """
        if self.total:
            return min(1.0, self.progress / self.total)
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
        self.update(advance=advance)

    def update(
        self,
        *,
        total: None | float | UnusedParameter = UNUSED,
        progress: float | UnusedParameter = UNUSED,
        advance: float | UnusedParameter = UNUSED,
    ) -> None:
        """Update the progress bar with the given options.

        Example:
            ```py
            progress_bar.update(
                total=200,  # Set new total to 200 steps.
                progress=50,  # Set the progress to 50 (out of 200).
            )
            ```

        Args:
            total: New total number of steps.
            progress: Set the progress to the given number of steps.
            advance: Advance the progress by this number of steps.
        """
        if not isinstance(total, UnusedParameter):
            if total != self.total:
                self._eta.reset()
            self.total = total

        if not isinstance(progress, UnusedParameter):
            self.progress = progress

        if not isinstance(advance, UnusedParameter):
            self.progress += advance

        if self.progress is not None and self.total is not None:
            self._eta.add_sample(self.progress / self.total)

        self._display_eta = self._eta.eta
