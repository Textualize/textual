from __future__ import annotations

from rich.cells import cell_len
from rich.segment import Segment
from rich.style import Style

from ._types import Lines
from .draw import DrawStyle


def render_outline(
    lines: Lines,
    width: int,
    sides: tuple[bool, bool, bool, bool],
    draw: DrawStyle,
    style: Style,
) -> None:
    top, right, bottom, left = sides

    top_chars, mid_chars, bottom_chars = ("┏━┓", "┃ ┃", "┗━┛")

    mid_top = 0
    mid_end = len(lines)

    if len(lines) < 2 or width < 2:
        return

    if top:
        row = top_chars[1] * width
        if left:
            row = top_chars[0] + row[1:]
        if right:
            row = row[:-1] + top_chars[2]
        lines[0] = [Segment(row, style)]
        mid_top += 1

    if bottom:
        row = bottom_chars[1] * width
        if left:
            row = bottom_chars[0] + row[1:]
        if right:
            row = row[:-1] + bottom_chars[2]
        lines[-1] = [Segment(row, style)]
        mid_end -= 1

    if left and right:
        left_char = mid_chars[0]
        right_char = mid_chars[2]
        for line in lines[mid_top:mid_end]:
            (
                _,
                line_contents,
            ) = Segment.divide(line, [1, width - 1])
            line[:] = [
                Segment(left_char, style),
                *line_contents,
                Segment(right_char, style),
            ]
    elif left:
        left_char = mid_chars[0]
        for line in lines[mid_top:mid_end]:
            _, line_contents = Segment.divide(line, [1, width])
            line[:] = [
                Segment(left_char, style),
                *line_contents,
            ]
    elif right:
        right_char = mid_chars[2]
        for line in lines[mid_top:mid_end]:
            line_contents, _ = Segment.divide(line, [width - 1, width])
            line[:] = [*line_contents, Segment(right_char, style)]


if __name__ == "__main__":
    from rich.console import Console
    from rich.segment import SegmentLines
    from rich.style import Style
    from rich.text import Text

    console = Console()
    text = Text("Textual " * 100)

    lines = console.render_lines(text, console.options)

    render_outline(
        lines,
        console.width,
        (True, True, True, True),
        DrawStyle.SQUARE,
        Style(color="green"),
    )

    console.print(SegmentLines(lines, new_lines=True))
