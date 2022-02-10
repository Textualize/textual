from __future__ import annotations

import statistics
from typing import Sequence, Iterable, Callable, TypeVar

from rich.color import Color
from rich.console import ConsoleOptions, Console, RenderResult
from rich.segment import Segment
from rich.style import Style

T = TypeVar("T", int, float)


class Sparkline:
    """A sparkline representing a series of data.

    Args:
        data (Sequence[T]): The sequence of data to render.
        width (int, optional): The width of the sparkline/the number of buckets to partition the data into.
        min_color (Color, optional): The color of values equal to the min value in data.
        max_color (Color, optional): The color of values equal to the max value in data.
        summary_function (Callable[list[T]]): Function that will be applied to each bucket.
    """

    BARS = "▁▂▃▄▅▆▇█"

    def __init__(
        self,
        data: Sequence[T],
        *,
        width: int | None,
        min_color: Color = Color.from_rgb(0, 255, 0),
        max_color: Color = Color.from_rgb(255, 0, 0),
        summary_function: Callable[[list[T]], float] = max,
    ) -> None:
        self.data = data
        self.width = width
        self.min_color = Style.from_color(min_color)
        self.max_color = Style.from_color(max_color)
        self.summary_function = summary_function

    @classmethod
    def _buckets(cls, data: Sequence[T], num_buckets: int) -> Iterable[list[T]]:
        """Partition ``data`` into ``num_buckets`` buckets. For example, the data
        [1, 2, 3, 4] partitioned into 2 buckets is [[1, 2], [3, 4]].

        Args:
            data (Sequence[T]): The data to partition.
            num_buckets (int): The number of buckets to partition the data into.
        """
        num_steps, remainder = divmod(len(data), num_buckets)
        for i in range(num_buckets):
            start = i * num_steps + min(i, remainder)
            end = (i + 1) * num_steps + min(i + 1, remainder)
            partition = data[start:end]
            if partition:
                yield partition

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        width = self.width or options.max_width
        len_data = len(self.data)
        if len_data == 0:
            yield Segment("▁" * width, style=self.min_color)
            return
        if len_data == 1:
            yield Segment("█" * width, style=self.max_color)
            return

        minimum, maximum = min(self.data), max(self.data)
        extent = maximum - minimum or 1

        buckets = list(self._buckets(self.data, num_buckets=self.width))

        bucket_index = 0
        bars_rendered = 0
        step = len(buckets) / width
        summary_function = self.summary_function
        min_color, max_color = self.min_color.color, self.max_color.color
        while bars_rendered < width:
            partition = buckets[int(bucket_index)]
            partition_summary = summary_function(partition)
            height_ratio = (partition_summary - minimum) / extent
            bar_index = int(height_ratio * (len(self.BARS) - 1))
            bar_color = _blend_colors(min_color, max_color, height_ratio)
            bars_rendered += 1
            bucket_index += step
            yield Segment(text=self.BARS[bar_index], style=Style.from_color(bar_color))


def _blend_colors(color1: Color, color2: Color, ratio: float) -> Color:
    """Given two RGB colors, return a color that sits some distance between
    them in RGB color space.

    Args:
        color1 (Color): The first color.
        color2 (Color): The second color.
        ratio (float): The ratio of color1 to color2.

    Returns:
        Color: A Color representing the blending of the two supplied colors.
    """
    r1, g1, b1 = color1.triplet
    r2, g2, b2 = color2.triplet
    dr = r2 - r1
    dg = g2 - g1
    db = b2 - b1
    return Color.from_rgb(
        red=r1 + dr * ratio, green=g1 + dg * ratio, blue=b1 + db * ratio
    )


if __name__ == "__main__":
    console = Console()

    def last(l):
        return l[-1]

    funcs = min, max, last, statistics.median, statistics.mean
    nums = [10, 2, 30, 60, 45, 20, 7, 8, 9, 10, 50, 13, 10, 6, 5, 4, 3, 7, 20]
    console.print(f"data = {nums}\n")
    for f in funcs:
        console.print(
            f"{f.__name__}:\t", Sparkline(nums, width=12, summary_function=f), end=""
        )
        console.print("\n")
