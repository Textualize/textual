from __future__ import annotations

from rich.console import Console, ConsoleOptions, RenderResult
from rich.measure import Measurement
from rich.segment import Segment
from rich.style import Style, StyleType

DIGITS = " 0123456789+-^x:ABCDEF$£€()"
DIGITS3X3_BOLD = """\



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

╭─╮
├─┤
╵ ╵
┌─╮
├─┤
└─╯
╭─╮
│
╰─╯
┌─╮
│ │
└─╯
╭─╴
├─
╰─╴
╭─╴
├─
╵
╭╫╮
╰╫╮
╰╫╯
╭─╮
╪═
┴─╴
╭─╮
╪═
╰─╯
╭╴ 
│  
╰╴ 
 ╶╮ 
  │ 
 ╶╯ 
""".splitlines()


DIGITS3X3 = """\



╭─╮
│ │
╰─╯
╶╮
 │
╶┴╴
╶─╮
┌─┘
╰─╴
╶─╮
 ─┤
╶─╯
╷ ╷
╰─┤
  ╵
╭─╴
╰─╮
╶─╯
╭─╴
├─╮
╰─╯
╶─┐
  │
  ╵
╭─╮
├─┤
╰─╯
╭─╮
╰─┤
╶─╯

╶┼╴


╶─╴

 ^



 ×


 :

╭─╮
├─┤
╵ ╵
┌─╮
├─┤
└─╯
╭─╮
│
╰─╯
┌─╮
│ │
└─╯
╭─╴
├─
╰─╴
╭─╴
├─
╵
╭╫╮
╰╫╮
╰╫╯
╭─╮
╪═
┴─╴
╭─╮
╪═
╰─╯
╭╴ 
│  
╰╴ 
 ╶╮ 
  │ 
 ╶╯ 
""".splitlines()


class Digits:
    """Renders a 3X3 unicode 'font' for numerical values.

    Args:
        text: Text to display.
        style: Style to apply to the digits.

    """

    REPLACEMENTS = str.maketrans({".": "•"})

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
            style: Rich Style.

        Returns:
            Result of render.
        """
        digit_pieces: list[list[str]] = [[], [], []]
        row1 = digit_pieces[0].append
        row2 = digit_pieces[1].append
        row3 = digit_pieces[2].append

        if style.bold:
            digits = DIGITS3X3_BOLD
        else:
            digits = DIGITS3X3

        for character in self._text.translate(self.REPLACEMENTS):
            try:
                position = DIGITS.index(character) * 3
            except ValueError:
                row1(" ")
                row2(" ")
                row3(character)
            else:
                row1(digits[position].ljust(3))
                row2(digits[position + 1].ljust(3))
                row3(digits[position + 2].ljust(3))

        new_line = Segment.line()
        for line in digit_pieces:
            yield Segment("".join(line), style)
            yield new_line

    @classmethod
    def get_width(cls, text: str) -> int:
        """Calculate the width without rendering.

        Args:
            text: Text which may be displayed in the `Digits` widget.

        Returns:
            width of the text (in cells).
        """
        width = sum(3 if character in DIGITS else 1 for character in text)
        return width

    def __rich_measure__(
        self, console: Console, options: ConsoleOptions
    ) -> Measurement:
        width = self.get_width(self._text)
        return Measurement(width, width)
