from __future__ import annotations

from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.measure import Measurement
from rich.padding import Padding
from rich.segment import Segment, SegmentLines

from ._box import BOX_STYLES


class Outline:
    def __init__(
        self,
        renderable: RenderableType,
        sides: tuple[str, str, str, str],
        styles: tuple[str, str, str, str],
    ) -> None:
        self.renderable = renderable
        self.sides = sides
        self.styles = styles

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        width = options.max_width
        renderable = Padding(self.renderable, 1)
        lines = console.render_lines(renderable, options)

        top, right, bottom, left = self.sides
        top_style, right_style, bottom_style, left_style = map(
            console.get_style, self.styles
        )

        BOX = BOX_STYLES

        mid_top = 0
        mid_end = len(lines)

        if len(lines) < 2 or width < 2:
            yield SegmentLines(lines, new_lines=True)
            return

        if top != "none":
            top_chars = BOX[top][0]
            row = top_chars[1] * width
            if left:
                row = top_chars[0] + row[1:]
            if right:
                row = row[:-1] + top_chars[2]

            lines[0] = [Segment(row, top_style)]
            mid_top += 1

        if bottom != "none":
            bottom_chars = BOX[bottom][2]
            row = bottom_chars[1] * width
            if left:
                row = bottom_chars[0] + row[1:]
            if right:
                row = row[:-1] + bottom_chars[2]

            lines[-1] = [Segment(row, bottom_style)]
            mid_end -= 1

        if left != "none" and right != "none":
            left_char = BOX[left][1][0]
            right_char = BOX[right][1][2]
            for line in lines[mid_top:mid_end]:
                _, line_contents = Segment.divide(line, [1, width - 1])
                line[:] = [
                    Segment(left_char, left_style),
                    *line_contents,
                    Segment(right_char, right_style),
                ]
        elif left != "none":
            left_char = BOX[left][1][0]
            for line in lines[mid_top:mid_end]:
                _, line_contents = Segment.divide(line, [1, width])
                line[:] = [
                    Segment(left_char, left_style),
                    *line_contents,
                ]
        elif right != "none":
            right_char = BOX[right][1][2]
            for line in lines[mid_top:mid_end]:
                line_contents, _ = Segment.divide(line, [width - 1, width])
                line[:] = [*line_contents, Segment(right_char, right_style)]

        yield SegmentLines(lines, new_lines=True)

    def __rich_measure__(
        self, console: "Console", options: ConsoleOptions
    ) -> Measurement:
        return Measurement.get(console, options, self.renderable)


if __name__ == "__main__":
    from rich.console import Console
    from rich.segment import SegmentLines
    from rich.style import Style
    from rich.text import Text
    from rich.traceback import install

    install(show_locals=True)

    console = Console()
    text = Text("Textual " * 30, style="dim")

    outline = Outline(text, ("", "outer", "", "outer"), ("", "red", "", "green"))

    console.print(Padding(outline, 1))

    outline = Outline(
        text,
        ("dashed", "dashed", "dashed", "dashed"),
        ("green", "green", "green", "green"),
    )
    console.print(Padding(outline, 1))

    # lines = console.render_lines(text, console.options)

    # render_outline(
    #     lines,
    #     console.width,
    #     (True, True, True, True),
    #     DrawStyle.SQUARE,
    #     Style(color="green"),
    # )

    # console.print(SegmentLines(lines, new_lines=True))
