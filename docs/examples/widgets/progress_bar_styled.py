from textual.app import App, ComposeResult
from textual.containers import Center, Middle
from textual.timer import Timer
from textual.widgets import Footer, ProgressBar


class StyledProgressBar(App[None]):
    BINDINGS = [("s", "start", "Start")]
    CSS_PATH = "progress_bar_styled.tcss"

    progress_timer: Timer
    """Timer to simulate progress happening."""

    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                yield ProgressBar()
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


if __name__ == "__main__":
    StyledProgressBar().run()
