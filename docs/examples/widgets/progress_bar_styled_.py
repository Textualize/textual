from textual.app import App, ComposeResult
from textual.clock import MockClock
from textual.containers import Center, Middle
from textual.timer import Timer
from textual.widgets import Footer, ProgressBar


class StyledProgressBar(App[None]):
    BINDINGS = [("s", "start", "Start")]
    CSS_PATH = "progress_bar_styled.tcss"

    progress_timer: Timer
    """Timer to simulate progress happening."""

    def compose(self) -> ComposeResult:
        self.clock = MockClock()
        with Center():
            with Middle():
                yield ProgressBar(clock=self.clock)
        yield Footer()

    def on_mount(self) -> None:
        """Set up a timer to simulate progress happening."""
        self.progress_timer = self.set_interval(1 / 10, self.make_progress, pause=True)

    def make_progress(self) -> None:
        """Called automatically to advance the progress bar."""
        self.query_one(ProgressBar).advance(1)

    def action_start(self) -> None:
        """Start the progress tracking."""
        self.query_one(ProgressBar).update(total=100)
        self.progress_timer.resume()
        self.query_one(ProgressBar).refresh()

    def key_f(self) -> None:
        # Freeze time for the indeterminate progress bar.
        self.clock.set_time(5.0)

    def key_t(self) -> None:
        # Freeze time to show always the same ETA.
        self.clock.set_time(0)
        self.query_one(ProgressBar).update(total=100, progress=0)
        self.clock.set_time(3.9)
        self.query_one(ProgressBar).update(progress=39)

    def key_u(self) -> None:
        self.query_one(ProgressBar).update(total=100, progress=100)


if __name__ == "__main__":
    StyledProgressBar().run()
