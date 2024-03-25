from textual.app import App, ComposeResult
from textual.widgets import ProgressBar


class TooltipApp(App[None]):
    def compose(self) -> ComposeResult:
        progress_bar = ProgressBar(100, show_eta=False)
        progress_bar.advance(10)
        progress_bar.tooltip = "Hello, Tooltip!"
        yield progress_bar


if __name__ == "__main__":
    app = TooltipApp()
    app.run()
