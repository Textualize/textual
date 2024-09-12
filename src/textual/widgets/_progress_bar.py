"""Implements a progress bar widget."""

from __future__ import annotations

from typing import Optional

from rich.style import Style

from textual._types import UnusedParameter
from textual.app import ComposeResult, RenderResult
from textual.clock import Clock
from textual.color import Gradient
from textual.eta import ETA
from textual.geometry import clamp
from textual.reactive import reactive
from textual.renderables.bar import Bar as BarRenderable
from textual.widget import Widget
from textual.widgets import Label

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

    percentage: reactive[float | None] = reactive[Optional[float]](None)
    """The percentage of progress that has been completed."""

    gradient: reactive[Gradient | None] = reactive(None)
    """An optional gradient."""

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        clock: Clock | None = None,
        gradient: Gradient | None = None,
    ):
        """Create a bar for a [`ProgressBar`][textual.widgets.ProgressBar]."""
        self._clock = (clock or Clock()).clone()
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.set_reactive(Bar.gradient, gradient)

    def _validate_percentage(self, percentage: float | None) -> float | None:
        """Avoid updating the bar, if the percentage increase is too small to render."""
        width = self.size.width * 2
        return (
            None
            if percentage is None
            else (int(percentage * width) / width if width else percentage)
        )

    def watch_percentage(self, percentage: float | None) -> None:
        """Manage the timer that enables the indeterminate bar animation."""
        if percentage is not None:
            self.auto_refresh = None
        else:
            self.auto_refresh = 1 / 15

    def render(self) -> RenderResult:
        """Render the bar with the correct portion filled."""
        if self.percentage is None:
            return self.render_indeterminate()
        else:
            bar_style = (
                self.get_component_rich_style("bar--bar")
                if self.percentage < 1
                else self.get_component_rich_style("bar--complete")
            )
            return BarRenderable(
                highlight_range=(0, self.size.width * self.percentage),
                highlight_style=Style.from_color(bar_style.color),
                background_style=Style.from_color(bar_style.bgcolor),
                gradient=self.gradient,
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
            start = (speed * self._clock.time) % (2 * total_imaginary_width)
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


class PercentageStatus(Label):
    """A label to display the percentage status of the progress bar."""

    DEFAULT_CSS = """
    PercentageStatus {
        width: 5;
        content-align-horizontal: right;
    }
    """

    percentage: reactive[int | None] = reactive[Optional[int]](None)
    """The percentage of progress that has been completed."""

    def _validate_percentage(self, percentage: float | None) -> int | None:
        return None if percentage is None else round(percentage * 100)

    def render(self) -> RenderResult:
        return "--%" if self.percentage is None else f"{self.percentage}%"


class ETAStatus(Label):
    """A label to display the estimated time until completion of the progress bar."""

    DEFAULT_CSS = """
    ETAStatus {
        width: 9;
        content-align-horizontal: right;
    }
    """
    eta: reactive[float | None] = reactive[Optional[float]](None)
    """Estimated number of seconds till completion, or `None` if no estimate is available."""

    def render(self) -> RenderResult:
        """Render the ETA display."""
        eta = self.eta
        if eta is None:
            return "--:--:--"
        else:
            minutes, seconds = divmod(round(eta), 60)
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

    gradient: reactive[Gradient | None] = reactive(None)
    """Optional gradient object (will replace CSS styling in bar)."""

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
        clock: Clock | None = None,
        gradient: Gradient | None = None,
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
            clock: An optional clock object (leave as default unless testing).
            gradient: An optional Gradient object (will replace CSS styles in the bar).
        """
        self._clock = clock or Clock()
        self._eta = ETA()
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.total = total
        self.show_bar = show_bar
        self.show_percentage = show_percentage
        self.show_eta = show_eta
        self.set_reactive(ProgressBar.gradient, gradient)

    def on_mount(self) -> None:
        self.update()
        self.set_interval(1, self.update)
        self._clock.reset()

    def compose(self) -> ComposeResult:
        if self.show_bar:
            yield (
                Bar(id="bar", clock=self._clock)
                .data_bind(ProgressBar.percentage)
                .data_bind(ProgressBar.gradient)
            )
        if self.show_percentage:
            yield PercentageStatus(id="percentage").data_bind(ProgressBar.percentage)
        if self.show_eta:
            yield ETAStatus(id="eta").data_bind(eta=ProgressBar._display_eta)

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
            return clamp(self.progress / self.total, 0.0, 1.0)
        elif self.total == 0:
            return 1.0
        return None

    def _watch_progress(self, progress: float) -> None:
        """Perform update when progress is modified."""
        self.update(progress=progress)

    def _watch_total(self, total: float) -> None:
        """Update when the total is modified."""
        self.update(total=total)

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
        current_time = self._clock.time
        if not isinstance(total, UnusedParameter):
            if total is None or total != self.total:
                self._eta.reset()
            self.total = total

        def add_sample() -> None:
            """Add a new sample."""
            if self.progress is not None and self.total:
                self._eta.add_sample(current_time, self.progress / self.total)

        if not isinstance(progress, UnusedParameter):
            self.progress = progress
            add_sample()

        if not isinstance(advance, UnusedParameter):
            self.progress += advance
            add_sample()

        self._display_eta = (
            None if self.total is None else self._eta.get_eta(current_time)
        )
