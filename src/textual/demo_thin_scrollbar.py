from __future__ import annotations

from math import ceil

from rich.color import Color
from rich.segment import Segment, Segments
from rich.style import Style

from textual.app import App, ComposeResult
from textual.scrollbar import ScrollBar, ScrollBarRender
from textual.containers import Vertical
from textual.widgets import Footer, Header, Static


class ThinScrollBarRender(ScrollBarRender):
    @classmethod
    def render_bar(
        cls,
        size: int = 25,
        virtual_size: float = 50,
        window_size: float = 20,
        position: float = 0,
        thickness: int = 1,
        vertical: bool = True,
        back_color: Color = Color.parse("#555555"),
        bar_color: Color = Color.parse("bright_magenta"),
    ) -> Segments:
        if vertical or thickness > 1:
            return super().render_bar(
                size=size,
                virtual_size=virtual_size,
                window_size=window_size,
                position=position,
                thickness=thickness,
                vertical=vertical,
                back_color=back_color,
                bar_color=bar_color,
            )

        assert not vertical
        assert thickness == 1

        _Style = Style
        _Segment = Segment

        norm_style = _Style(bgcolor=back_color, color=bar_color)

        bars_start = ["▝", " "]
        bars_start_style = norm_style
        bars_end = ["▘", " "]
        bars_end_style = norm_style
        blank = " "
        blank_style = norm_style
        full = "▀"
        full_style = norm_style

        assert len(bars_end) == len(bars_start)

        len_bars = len(bars_start)

        upper_meta = {"@mouse.up": "scroll_up"}
        middle_meta = {"@mouse.up": "release", "@mouse.down": "grab"}
        lower_meta = {"@mouse.up": "scroll_down"}

        upper_back_style = blank_style + _Style.from_meta(upper_meta)
        middle_fg_style = full_style + _Style.from_meta(middle_meta)
        lower_back_style = blank_style + _Style.from_meta(lower_meta)

        upper_back_segment = _Segment(blank, upper_back_style)
        middle_fg_segment = _Segment(full, middle_fg_style)
        lower_back_segment = _Segment(blank, lower_back_style)

        if window_size and size and virtual_size and size != virtual_size:
            step_size = virtual_size / size

            start = int(position / step_size * len_bars)
            end = start + max(len_bars, int(ceil(window_size / step_size * len_bars)))

            start_index, start_bar = divmod(max(0, start), len_bars)
            end_index, end_bar = divmod(max(0, end), len_bars)

            segments = (
                [lower_back_segment] * (start_index)
                + [middle_fg_segment] * (end_index - start_index)
                + [upper_back_segment] * (size - end_index)
            )

            # Apply the smaller bar characters to head and tail of scrollbar for more "granularity"
            if start_index < len(segments):
                start_bar_character = bars_start[len_bars - 1 - start_bar]
                if start_bar_character != " ":
                    segments[start_index] = _Segment(
                        start_bar_character,
                        bars_start_style + _Style.from_meta(middle_meta),
                    )
            if end_index < len(segments):
                end_bar_character = bars_end[len_bars - 1 - end_bar]
                if end_bar_character != " ":
                    segments[end_index] = _Segment(
                        end_bar_character,
                        bars_end_style + _Style.from_meta(middle_meta),
                    )
        else:
            segments = [_Segment(blank, blank_style)] * int(size)

        return Segments((segments + [_Segment.line()]), new_lines=False)


class MyTextBox(Vertical):
    DEFAULT_CSS = """
    MyTextBox {
        background: $panel;
        width: 20;
        height: 10;
        overflow: scroll;
    }
    MyTextBox > Static {
        width: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static(
            "\n".join(
                f"{i:2} a somewhat long line that exceeds width {i:2}"
                for i in range(1, 21)
            )
        )


class ThinScrollBarDemoApp(App[None]):
    TITLE = "Thin ScrollBar Demo"
    DEFAULT_CSS = """
    MyTextBox { margin: 1 1 1 1; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            MyTextBox(id="box1"),
            MyTextBox(id="box2"),
            MyTextBox(id="box3"),
        )
        yield Footer()

    def on_mount(self) -> None:
        # ... and because ScrollBar uses `self.renderer` rather than
        # `type(self).renderer` (that's intentional), we can even do this:
        self.query_one(
            "#box2", MyTextBox
        ).horizontal_scrollbar.renderer = ScrollBarRender


app = ThinScrollBarDemoApp()
ScrollBar.renderer = ThinScrollBarRender
if __name__ == "__main__":
    app.run()
