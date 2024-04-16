from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Digits, ProgressBar


class Numbers(Vertical):

    DEFAULT_CSS = """
    Digits {
        border: red;
    }
    """

    def __init__(self, numbers: list[int]) -> None:
        self.numbers = numbers
        super().__init__()

    def compose(self) -> ComposeResult:
        with Horizontal():
            for number in self.numbers:
                yield Digits(str(number))


class Progress(Horizontal):

    progress = reactive(0, recompose=True)

    def compose(self) -> ComposeResult:
        bar = ProgressBar(100, show_eta=False)
        bar.progress = self.progress
        yield bar


class RecomposeApp(App):

    start = reactive(0, recompose=True)
    end = reactive(5, recompose=True)
    progress: reactive[int] = reactive(0, recompose=True)

    def compose(self) -> ComposeResult:
        yield Numbers(list(range(self.start, self.end)))
        yield Progress().data_bind(RecomposeApp.progress)

    def on_mount(self) -> None:
        self.start = 10
        self.end = 17
        # Call update_progress later so it is part of another recompose
        self.set_timer(0.05, self.update_progress)

    def update_progress(self) -> None:
        self.progress = 50


if __name__ == "__main__":
    app = RecomposeApp()
    app.run()
