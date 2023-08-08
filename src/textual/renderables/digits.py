from __future__ import annotations

from rich.console import Console, ConsoleOptions, RenderResult
from rich.measure import Measurement
from rich.segment import Segment
from rich.style import Style, StyleType

DIGITS = r" 0123456789+-.%ex,"
DIGITS3X3 = """\



┏━┓
┃ ┃
┗━┛
 ┓
 ┃
╺┻╸
╺━┓
┏━┛
┗━╸
╺━┓
 ━┫
╺━┛
╻ ╻
┗━┫
  ╹
┏━╸
┗━┓
╺━┛
┏━╸
┣━┓
┗━┛
╺━┓
  ┃
  ╹
┏━┓
┣━┫
┗━┛
┏━┓
┗━┫
╺━┛

╺╋╸


╺━╸



.

 %



e

x



,
""".splitlines()
DIGIT_WIDTHS = {".": 1, "x": 1, "e": 1, ",": 1}


class Digits:
    """Renders a 3X3 unicode 'font' for numerical values."""

    def __init__(self, text: str, style: StyleType = "") -> None:
        self._text = text
        self._style = style

    @classmethod
    def _filter_text(cls, text: str) -> str:
        """Remove any unsupported characters."""
        return "".join(
            (character if character in DIGITS else " ")
            for character in text
            if character in DIGITS
        )

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        style = console.get_style(self._style)
        yield from self.render(style)

    def render(self, style: Style) -> RenderResult:
        """Render with the given style

        Args:
            style: Rich Style

        """
        segments: list[list[Segment]] = [[], [], []]
        _Segment = Segment
        row1 = segments[0].append
        row2 = segments[1].append
        row3 = segments[2].append

        for character in self._filter_text(self._text):
            try:
                position = DIGITS.index(character) * 3
            except ValueError:
                continue
            width = DIGIT_WIDTHS.get(character, 3)
            line1, line2, line3 = [
                line.ljust(width) for line in DIGITS3X3[position : position + 3]
            ]
            row1(_Segment(line1, style))
            row2(_Segment(line2, style))
            row3(_Segment(line3, style))

        new_line = Segment.line()
        for line in segments:
            yield from line
            yield new_line

    @classmethod
    def get_width(cls, text: str) -> int:
        """Calculate the width without rendering."""
        text = cls._filter_text(text)
        width = sum(DIGIT_WIDTHS.get(character, 3) for character in text)
        return width

    def __rich_measure__(
        self, console: Console, options: ConsoleOptions
    ) -> Measurement:
        width = self.get_width(self._text)
        return Measurement(width, width)


if __name__ == "__main__":
    from rich import print

    print(Digits("3x10e4%", "white on blue"))
