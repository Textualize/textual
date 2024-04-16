from __future__ import annotations

import statistics
from fractions import Fraction
from typing import Callable, Generic, Iterable, Sequence, TypeVar

from rich.color import Color
from rich.console import Console, ConsoleOptions, RenderResult
from rich.segment import Segment
from rich.style import Style

from textual.renderables._blend_colors import blend_colors

T = TypeVar("T", int, float)

SummaryFunction = Callable[[Sequence[T]], float]


class Sparkline(Generic[T]):
    """A sparkline representing a series of data.

    Args:
        data: The sequence of data to render.
        width: The width of the sparkline/the number of buckets to partition the data into.
        min_color: The color of values equal to the min value in data.
        max_color: The color of values equal to the max value in data.
        summary_function: Function that will be applied to each bucket.
    """

    BARS = "▁▂▃▄▅▆▇█"

    def __init__(
        self,
        data: Sequence[T],
        *,
        width: int | None,
        min_color: Color = Color.from_rgb(0, 255, 0),
        max_color: Color = Color.from_rgb(255, 0, 0),
        summary_function: SummaryFunction[T] = max,
    ) -> None:
        self.data: Sequence[T] = data
        self.width = width
        self.min_color = Style.from_color(min_color)
        self.max_color = Style.from_color(max_color)
        self.summary_function: SummaryFunction[T] = summary_function

    @classmethod
    def _buckets(cls, data: list[T], num_buckets: int) -> Iterable[Sequence[T]]:
        """Partition ``data`` into ``num_buckets`` buckets. For example, the data
        [1, 2, 3, 4] partitioned into 2 buckets is [[1, 2], [3, 4]].

        Args:
            data: The data to partition.
            num_buckets: The number of buckets to partition the data into.
        """
        bucket_step = Fraction(len(data), num_buckets)
        for bucket_no in range(num_buckets):
            start = int(bucket_step * bucket_no)
            end = int(bucket_step * (bucket_no + 1))
            partition = data[start:end]
            if partition:
                yield partition

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        width = self.width or options.max_width
        len_data = len(self.data)
        if len_data == 0:
            yield Segment("▁" * width, self.min_color)
            return
        if len_data == 1:
            yield Segment("█" * width, self.max_color)
            return

        minimum, maximum = min(self.data), max(self.data)
        extent = maximum - minimum or 1

        buckets = tuple(self._buckets(list(self.data), num_buckets=width))

        bucket_index = 0.0
        bars_rendered = 0
        step = len(buckets) / width
        summary_function = self.summary_function
        min_color, max_color = self.min_color.color, self.max_color.color
        assert min_color is not None
        assert max_color is not None
        while bars_rendered < width:
            partition = buckets[int(bucket_index)]
            partition_summary = summary_function(partition)
            height_ratio = (partition_summary - minimum) / extent
            bar_index = int(height_ratio * (len(self.BARS) - 1))
            bar_color = blend_colors(min_color, max_color, height_ratio)
            bars_rendered += 1
            bucket_index += step
            yield Segment(self.BARS[bar_index], Style.from_color(bar_color))


if __name__ == "__main__":
    console = Console()

    def last(l: Sequence[T]) -> T:
        return l[-1]

    funcs: Sequence[SummaryFunction[int]] = (
        min,
        max,
        last,
        statistics.median,
        statistics.mean,
    )
    nums = [10, 2, 30, 60, 45, 20, 7, 8, 9, 10, 50, 13, 10, 6, 5, 4, 3, 7, 20]
    console.print(f"data = {nums}\n")
    for f in funcs:
        console.print(
            f"{f.__name__}:\t",
            Sparkline(nums, width=12, summary_function=f),
            end="",
        )
        console.print("\n")
