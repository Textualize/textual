from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Horizontal, Vertical


_character_map: dict[str, str] = {}

# in the mappings below, we use underscores to make spaces more visible,
# we will strip them out later
_character_map[
    "0"
] = """
┏━┓
┃╱┃
┗━┛
"""

_character_map[
    "1"
] = """
·┓·
 ┃·
╺┻╸
"""

_character_map[
    "2"
] = """
╺━┓
┏━┛
┗━╸
"""

_character_map[
    "3"
] = """
╺━┓
 ━┫
╺━┛
"""

_character_map[
    "4"
] = """
╻ ╻
┗━┫
  ╹
"""

_character_map[
    "5"
] = """
┏━╸
┗━┓
╺━┛
"""

_character_map[
    "6"
] = """
┏━╸
┣━┓
┗━┛
"""

_character_map[
    "7"
] = """
╺━┓
  ┃
  ╹
"""

_character_map[
    "8"
] = """
┏━┓
┣━┫
┗━┛
"""

_character_map[
    "9"
] = """
┏━┓
┗━┫
╺━┛
"""

_character_map[
    " "
] = """
···
···
···
"""

_character_map[
    "A"
] = """
┏━┓
┣━┫
╹ ╹
"""

_character_map[
    "a"
] = """
·_·
╭━┫
╰━┗
"""

_character_map[
    "B"
] = """
┏━╮
┃━┫
┗━╯
"""

_character_map[
    "b"
] = """
╻  
┃━╮
┗━╯
"""

_character_map[
    "C"
] = """
┏━╸
┃··
┗━╸
"""

_character_map[
    "c"
] = """
···
╭━·
╰━·
"""

_character_map[
    "D"
] = """
┏━╮
┃ ┃
┗━╯
"""

_character_map[
    "d"
] = """
··╻
╭━┃
╰━╯
"""

_character_map[
    "E"
] = """
┏━╸
┣━ 
┗━╸
"""

_character_map[
    "e"
] = """
·_·
┢━·
╰━·
"""

_character_map[
    "F"
] = """
┏━╸
┣━╸
╹··
"""

_character_map[
    "f"
] = """
·┏·
·┃┚
┍┛·
·┃·
"""

_character_map[
    "G"
] = """
┏━╸
┃ ┓
┗━┛
"""

_character_map[
    "g"
] = """
···
╭━╮
╰━┫
·━┛
"""

_character_map[
    "H"
] = """
╻ ╻
┣━┫
╹ ╹
"""

_character_map[
    "h"
] = """
╻··
┣━┓
╹ ╹
"""

_character_map[
    "I"
] = """
·┳·
·┃·
·┻·
"""

_character_map[
    "i"
] = """
·•·
·╻·
·╹·
"""

_character_map[
    "J"
] = """
╺┳╸
 ┃·
╺┛·
"""

_character_map[
    "j"
] = """
·•·
·┳·
·┃·
·┛·
"""

_character_map[
    "K"
] = """
╻ ╻
┣━ 
╹ ╹
"""

_character_map[
    "L"
] = """
╻··
┃··
┗━╸
"""

_character_map[
    "l"
] = """
·╻·
·┃·
·┛·
"""

_character_map[
    "M"
] = """
╻ ╻
┣┏┫
╹ ╹
"""

_character_map[
    "m"
] = """
···
┣┏┓
╹ ╹
"""

_character_map[
    "N"
] = """
╻ ╻
┃╺┫
╹ ╹
"""

_character_map[
    "n"
] = """
···
┃━┓
╹ ╹
"""

_character_map[
    "O"
] = """
╭━╮
┃ ┃
╰━╯
"""

_character_map[
    "o"
] = """
···
╭━╮
╰━╯
"""

_character_map[
    "P"
] = """
┏━┓
┣━┛
╹··
"""

_character_map[
    "p"
] = """
···
┳━╮
┣━╯
╹··
"""

_character_map[
    "Q"
] = """
┏━┓
┃ ┃
┗┗╸
"""

_character_map[
    "q"
] = """
···
╭━╮
╰━┫
··┖
"""

_character_map[
    "R"
] = """
┏━┓
┣━┛
╹ ╹
"""

_character_map[
    "R"
] = """
··
┢━
╹ 
"""


_character_map[
    "S"
] = """
┏━╸
┗━┓
╺━┛
"""

_character_map[
    "s"
] = """
·_·
┗━╮
╺━╯
"""

_character_map[
    "T"
] = """
╺┳╸
 ┃·
 ╹·
"""

_character_map[
    "t"
] = """
·╻·
·╋·
 ┛·
"""

_character_map[
    "U"
] = """
╻ ╻
┃ ┃
┗━┛
"""
_character_map[
    "u"
] = """
···
╻ ╻
╰━┻
"""

_character_map[
    "V"
] = """
···
┃ ┃
·╹·
"""

_character_map[
    "v"
] = """
···
╻ ╻
·╹·
"""

_character_map[
    "W"
] = """
╻ ╻
┃ ┃
╹┻╹
"""

_character_map[
    "w"
] = """
···
╻ ╻
╹┻╹
"""

_character_map[
    "X"
] = """
╻ ╻
·╻·
╹ ╹
"""

_character_map[
    "x"
] = """
···
╻ ╻
_┻_
"""

_character_map[
    "Y"
] = """
╻ ╻
·╻·
·╹·
"""

_character_map[
    "y"
] = """
···
╻ ╻
·╻·
╹··
"""


_character_map[
    "Z"
] = """
╺━┓
·╻·
┗━╸
"""

_character_map[
    "z"
] = """
__·
·╻·
┗━╸
"""


_character_map[
    "."
] = """
·
·
╸
"""


_character_map[
    ","
] = """
·
·
╹
"""

_character_map[
    "+"
] = """
···
╺╋╸
···
"""

_character_map[
    "-"
] = """
···
╺━╸
···
"""

_character_map[
    "="
] = """
···
╺━╸
╺━╸
"""

_character_map["*"] = _character_map["X"]

_character_map[
    "/"
] = """
··╻
·╻·
╹··
"""

_character_map[
    "!"
] = """
·╻·
·╹·
·•·
"""

_character_map[
    "?"
] = """
┏━┓
·┏┛
·•·
"""

_character_map[
    "'"
] = """
╻
·
·
"""


_character_map[
    '"'
] = """
╻╻
··
··
"""

_character_map[
    ":"
] = """
··
·•
·•
"""

_character_map[
    ";"
] = """
·
•
╹
"""

_character_map[
    "("
] = """
··╸
·┃·
··╸
"""

_character_map[
    ")"
] = """
·╺·
··┃
·╺·
"""

_character_map[
    "["
] = """
·┏╸
·┃·
·┗╸
"""

_character_map[
    "]"
] = """
╺┓
·┃
╺┛
"""

_character_map[
    "{"
] = """
·┏╸
·┫·
·┗╸
"""

_character_map[
    "}"
] = """
╺┓
·┣
╺┛
"""

_character_map[
    "<"
] = """
··╸
·╸·
··╸
"""

_character_map[
    ">"
] = """
╺··
·╺·
╺··
"""

_character_map[
    "@"
] = """
╭━╮
╹╹┛
╰━·
"""

_character_map[
    "#"
] = """
╋╋
╋╋
···
"""


# here we strip spaces and replace underscores with spaces
_character_map = {k: v.strip().replace("·", " ") for k, v in _character_map.items()}


class SingleDigitDisplay(Static):
    digit = reactive(" ", layout=True)

    DEFAULT_CSS = """
        SingleDigitDisplay {
          height: 4;
          min-width: 2;
          max-width: 3;
        }
    """

    def __init__(self, initial_value=" ", always_upper=False, **kwargs):
        super().__init__(**kwargs)
        self.always_upper = always_upper
        self.digit = initial_value

    def watch_digit(self, digit: str) -> None:
        """Called when the digit attribute changes."""
        if len(digit) > 1:
            raise ValueError(f"Expected a single character, got {len(digit)}")
        if self.always_upper or (
            digit not in _character_map and digit.upper() in _character_map
        ):
            digit = digit.upper()
        self.update(_character_map[digit])


class LedDisplay(Widget):
    """A widget to display characters using 7-segment LED-like format."""

    digits = reactive("", layout=True)

    DEFAULT_CSS = """
    LedDisplay {
        layout: horizontal;
        height: 5;
    }
    """

    def __init__(self, initial_value="", **kwargs):
        super().__init__(**kwargs)
        self._displays = [SingleDigitDisplay(d) for d in initial_value]
        self.digits = initial_value
        self.previous_digits = initial_value

    def compose(self) -> ComposeResult:
        for led_display in self._displays:
            yield led_display

    def watch_digits(self, digits: str) -> None:
        """
        Called when the digits attribute changes.
        Here we update the display widgets to match the number of digits.
        """
        diff_digits_len = len(digits) - len(self._displays)
        if diff_digits_len > 0:
            # add new displays
            start = len(self._displays)
            for i in range(diff_digits_len):
                new_widget = SingleDigitDisplay(digits[start + i])
                self._displays.append(new_widget)
                self.mount(new_widget)
        elif diff_digits_len < 0:
            # remove displays
            for display in self._displays[diff_digits_len:]:
                display.remove()
                self._displays.remove(display)
        for i, d in enumerate(self.digits):
            self._displays[i].digit = d
