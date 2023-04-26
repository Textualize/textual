from textual.app import App, ComposeResult
from textual.containers import Center, Middle
from textual.widgets import ProgressBar


class IndeterminateProgressBar(App[None]):
    CSS_PATH = "progress_bar_styled.css"

    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                yield ProgressBar()

    def key_f(self) -> None:
        # Freeze time for the indeterminate progress bar.
        self.query_one(ProgressBar).query_one("#bar")._elapsed_time = lambda: 5

    def key_t(self) -> None:
        # Freeze time to show always the same ETA.
        self.query_one(ProgressBar).query_one("#eta")._elapsed_time = lambda: 4.2
        self.query_one(ProgressBar).update(total=100, progress=39)

    def key_u(self) -> None:
        self.query_one(ProgressBar).update(total=100, progress=100)


if __name__ == "__main__":
    IndeterminateProgressBar().run()
