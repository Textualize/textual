from textual.app import App, ComposeResult
from textual.containers import Center, Middle
from textual.widgets import ProgressBar


class IndeterminateProgressBar(App[None]):
    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                yield ProgressBar()

    def key_f(self) -> None:
        # Freeze time for the indeterminate progress bar.
        self.query_one(ProgressBar).query_one("#bar")._elapsed_time = lambda: 5

    def key_s(self) -> None:
        self.query_one(ProgressBar).query_one("#eta")._elapsed_time = lambda: 0
        self.query_one(ProgressBar).update(total=100)

    def key_t(self) -> None:
        self.query_one(ProgressBar).query_one("#eta")._elapsed_time = lambda: 1
        self.query_one(ProgressBar).update(progress=10)

    def key_u(self) -> None:
        self.query_one(ProgressBar).query_one("#eta")._elapsed_time = lambda: 4.2
        self.query_one(ProgressBar).update(progress=39)


if __name__ == "__main__":
    IndeterminateProgressBar().run()
