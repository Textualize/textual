import random
from statistics import mean

from textual.app import App, ComposeResult
from textual.widgets._sparkline import Sparkline

random.seed(73)
data = [random.expovariate(1 / 3) for _ in range(1000)]


class MyApp(App[None]):
    CSS_PATH = "sparkline.css"

    def compose(self) -> ComposeResult:
        yield Sparkline(data, summary_function=max)
        yield Sparkline(data, summary_function=mean)
        yield Sparkline(data, summary_function=min)


app = MyApp()
if __name__ == "__main__":
    app.run()
