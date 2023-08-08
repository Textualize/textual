from __future__ import annotations

from rich.console import Console, ConsoleOptions, RenderResult
from rich.measure import Measurement
from rich.segment import Segment
from rich.style import Style, StyleType

DIGITS = " 0123456789+-^x:"
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

 ^



 ×


 :

""".splitlines()


class Digits:
    """Renders a 3X3 unicode 'font' for numerical values."""

    def __init__(self, text: str, style: StyleType = "") -> None:
        self._text = text
        self._style = style

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
        segments: list[list[str]] = [[], [], []]
        row1 = segments[0].append
        row2 = segments[1].append
        row3 = segments[2].append

        for character in self._text:
            try:
                position = DIGITS.index(character) * 3
            except ValueError:
                row1(" ")
                row2(" ")
                row3(character)
            else:
                width = 3 if character in DIGITS else 1
                row1(DIGITS3X3[position].ljust(width))
                row2(DIGITS3X3[position + 1].ljust(width))
                row3(DIGITS3X3[position + 2].ljust(width))

        new_line = Segment.line()
        for line in segments:
            yield Segment("".join(line), style)
            yield new_line

    @classmethod
    def get_width(cls, text: str) -> int:
        """Calculate the width without rendering."""
        width = sum(3 if character in DIGITS else 1 for character in text)
        return width

    def __rich_measure__(
        self, console: Console, options: ConsoleOptions
    ) -> Measurement:
        width = self.get_width(self._text)
        return Measurement(width, width)


if __name__ == "__main__":
    from rich import print

    print(Digits("3x10e4%", "white on blue"))
