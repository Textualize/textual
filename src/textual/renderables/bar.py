from __future__ import annotations

from rich.console import Console, ConsoleOptions, RenderResult
from rich.style import Style, StyleType
from rich.text import Text

from textual.color import Gradient


class Bar:
    """Thin horizontal bar with a portion highlighted.

    Args:
        highlight_range: The range to highlight.
        highlight_style: The style of the highlighted range of the bar.
        background_style: The style of the non-highlighted range(s) of the bar.
        width: The width of the bar, or `None` to fill available width.
        gradient: Optional gradient object.
    """

    HALF_BAR_LEFT: str = "╺"
    BAR: str = "━"
    HALF_BAR_RIGHT: str = "╸"

    def __init__(
        self,
        highlight_range: tuple[float, float] = (0, 0),
        highlight_style: StyleType = "magenta",
        background_style: StyleType = "grey37",
        clickable_ranges: dict[str, tuple[int, int]] | None = None,
        width: int | None = None,
        gradient: Gradient | None = None,
    ) -> None:
        self.highlight_range = highlight_range
        self.highlight_style = highlight_style
        self.background_style = background_style
        self.clickable_ranges = clickable_ranges or {}
        self.width = width
        self.gradient = gradient

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        highlight_style = console.get_style(self.highlight_style)
        background_style = console.get_style(self.background_style)

        width = self.width or options.max_width
        start, end = self.highlight_range

        start = max(start, 0)
        end = min(end, width)

        output_bar = Text("", end="")

        if start == end == 0 or end < 0 or start > end:
            output_bar.append(Text(self.BAR * width, style=background_style, end=""))
            yield output_bar
            return

        # Round start and end to nearest half
        start = round(start * 2) / 2
        end = round(end * 2) / 2

        # Check if we start/end on a number that rounds to a .5
        half_start = start - int(start) > 0
        half_end = end - int(end) > 0

        # Initial non-highlighted portion of bar
        output_bar.append(
            Text(self.BAR * (int(start - 0.5)), style=background_style, end="")
        )
        if not half_start and start > 0:
            output_bar.append(Text(self.HALF_BAR_RIGHT, style=background_style, end=""))

        highlight_bar = Text("", end="")
        # The highlighted portion
        bar_width = int(end) - int(start)
        if half_start:
            highlight_bar.append(
                Text(
                    self.HALF_BAR_LEFT + self.BAR * (bar_width - 1),
                    style=highlight_style,
                    end="",
                )
            )
        else:
            highlight_bar.append(
                Text(self.BAR * bar_width, style=highlight_style, end="")
            )
        if half_end:
            highlight_bar.append(
                Text(self.HALF_BAR_RIGHT, style=highlight_style, end="")
            )

        if self.gradient is not None:
            _apply_gradient(highlight_bar, self.gradient, width)
        output_bar.append(highlight_bar)

        # The non-highlighted tail
        if not half_end and end - width != 0:
            output_bar.append(Text(self.HALF_BAR_LEFT, style=background_style, end=""))
        output_bar.append(
            Text(self.BAR * (int(width) - int(end) - 1), style=background_style, end="")
        )

        # Fire actions when certain ranges are clicked (e.g. for tabs)
        for range_name, (start, end) in self.clickable_ranges.items():
            output_bar.apply_meta(
                {"@click": f"range_clicked('{range_name}')"}, start, end
            )

        yield output_bar


def _apply_gradient(text: Text, gradient: Gradient, width: int) -> None:
    """Apply a gradient to a Rich Text instance.

    Args:
        text: A Text object.
        gradient: A Textual gradient.
        width: Width of gradient.
    """
    if not width:
        return
    assert width > 0
    from_color = Style.from_color
    get_rich_color = gradient.get_rich_color

    max_width = width - 1
    if not max_width:
        text.stylize(from_color(gradient.get_color(0).rich_color))
        return
    text_length = len(text)
    for offset in range(text_length):
        bar_offset = text_length - offset
        text.stylize(
            from_color(get_rich_color(bar_offset / max_width)),
            offset,
            offset + 1,
        )
