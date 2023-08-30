from math import sin

from textual.app import App, ComposeResult
from textual.widgets import Sparkline


class SparklineColorsApp(App[None]):
    CSS_PATH = "sparkline_colors.tcss"

    def compose(self) -> ComposeResult:
        nums = [abs(sin(x / 3.14)) for x in range(0, 360 * 6, 20)]
        yield Sparkline(nums, summary_function=max, id="fst")
        yield Sparkline(nums, summary_function=max, id="snd")
        yield Sparkline(nums, summary_function=max, id="trd")
        yield Sparkline(nums, summary_function=max, id="frt")
        yield Sparkline(nums, summary_function=max, id="fft")
        yield Sparkline(nums, summary_function=max, id="sxt")
        yield Sparkline(nums, summary_function=max, id="svt")
        yield Sparkline(nums, summary_function=max, id="egt")
        yield Sparkline(nums, summary_function=max, id="nnt")
        yield Sparkline(nums, summary_function=max, id="tnt")


app = SparklineColorsApp()
if __name__ == "__main__":
    app.run()
