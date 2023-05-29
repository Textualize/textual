from textual.app import App, ComposeResult
from textual.widgets._sparkline import Sparkline


class MyApp(App[None]):
    CSS_PATH = "sparkline_colors.css"

    def compose(self) -> ComposeResult:
        nums = [10, 2, 30, 60, 45, 20, 7, 8, 9, 10, 50, 13, 10, 6, 5, 4, 3, 7, 20]
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


app = MyApp()
if __name__ == "__main__":
    app.run()
