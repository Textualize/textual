import random
from statistics import mean

from textual.app import App, ComposeResult
from textual.widgets import Sparkline

random.seed(73)
data = [random.expovariate(1 / 3) for _ in range(1000)]


class SparklineApp(App[None]):
    DEFAULT_CSS = """
    SparklineApp {
        Sparkline {
            height: 1fr;
        }
    }
    """

    def compose(self) -> ComposeResult:
        yield Sparkline(data, summary_function=max)
        yield Sparkline(data, summary_function=mean)
        yield Sparkline(data, summary_function=min)


if __name__ == "__main__":
    app = SparklineApp()
    app.run()
