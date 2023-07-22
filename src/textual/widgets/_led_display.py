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
_┓_
 ┃_
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
___
___
___
"""

_character_map[
    "A"
] = """
┏━┓
┣━┫
╹ ╹
"""

_character_map["B"] = _character_map["8"]

_character_map[
    "B"
] = """
┏━╮
┃━┫
┗━╯
"""

_character_map[
    "C"
] = """
┏━╸
┃__
┗━╸
"""

_character_map[
    "D"
] = """
┏━╮
┃ ┃
┗━╯
"""


_character_map[
    "E"
] = """
┏━╸
┣━ 
┗━╸
"""

_character_map[
    "F"
] = """
┏━╸
┣━╸
╹__
"""

_character_map[
    "G"
] = """
┏━╸
┃ ┓
┗━┛
"""

_character_map[
    "H"
] = """
╻ ╻
┣━┫
╹ ╹
"""

_character_map[
    "I"
] = """
_╻_
_┃_
_╹_
"""

_character_map[
    "J"
] = """
╺┳╸
 ┃_
╺┛_
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
╻__
┃__
┗━╸
"""

_character_map[
    "M"
] = """
╻ ╻
┣┏┫
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
    "O"
] = """
╭━╮
┃ ┃
╰━╯
"""

_character_map[
    "P"
] = """
┏━┓
┣━┛
╹__
"""


_character_map[
    "Q"
] = """
┏━┓
┃ ┃
┗┗╸
"""

_character_map[
    "R"
] = """
┏━┓
┣━┛
╹ ╹
"""

_character_map["S"] = _character_map["5"]

_character_map[
    "T"
] = """
╺┳╸
 ┃_
 ╹_
"""

_character_map[
    "U"
] = """
╻ ╻
┃ ┃
┗━┛
"""

_character_map[
    "V"
] = """
╻ ╻
┃ ┃
_╹_
"""

_character_map[
    "W"
] = """
╻ ╻
┃╻┃
┗┻┛
"""

_character_map[
    "X"
] = """
╻ ╻
_╻_
╹ ╹
"""

_character_map[
    "Y"
] = """
╻ ╻
_╻_
_╹_
"""

_character_map[
    "Z"
] = """
╺━┓
_╻_
┗━╸
"""


_character_map[
    "."
] = """
_
_
╸
"""


_character_map[
    ","
] = """
_
_
╹
"""

_character_map[
    "+"
] = """
___
╺╋╸
___
"""

_character_map[
    "-"
] = """
___
╺━╸
___
"""

_character_map[
    "="
] = """
___
╺━╸
╺━╸
"""

_character_map["*"] = _character_map["X"]

_character_map[
    "/"
] = """
__╻
_╻_
╹__
"""

_character_map[
    "!"
] = """
_╻_
_╹_
_╹_
"""

_character_map[
    "?"
] = """
┏━┓
_╺┛
_╹_
"""

_character_map[
    "'"
] = """
╻
_
_
"""


_character_map[
    '"'
] = """
╻╻
__
__
"""

_character_map[
    ":"
] = """
_
╹
╹
"""

_character_map[
    ";"
] = """
_
╹
╸
"""

_character_map[
    "("
] = """
__╸
_┃_
__╸
"""

_character_map[
    ")"
] = """
_╺_
__┃
_╺_
"""

_character_map[
    "["
] = """
_┏╸
_┃_
_┗╸
"""

_character_map[
    "]"
] = """
╺┓
_┃
╺┛
"""

_character_map[
    "{"
] = """
_┏╸
_┫_
_┗╸
"""

_character_map[
    "}"
] = """
╺┓
_┣
╺┛
"""

_character_map[
    "<"
] = """
__╸
_╸_
__╸
"""

_character_map[
    ">"
] = """
╺__
_╺_
╺__
"""

_character_map[
    "@"
] = """
╭━╮
╹╹┛
╰━_
"""

_character_map[
    "#"
] = """
╋╋
╋╋
___
"""


# here we strip spaces and replace underscores with spaces
_character_map = {k: v.strip().replace("_", " ") for k, v in _character_map.items()}


class SingleDigitDisplay(Static):
    digit = reactive(" ", layout=True)

    DEFAULT_CSS = """
        SingleDigitDisplay {
          height: 3;
          max-width: 3;
        }
    """

    def __init__(self, initial_value=" ", **kwargs):
        super().__init__(**kwargs)
        self.digit = initial_value

    def watch_digit(self, digit: str) -> None:
        """Called when the digit attribute changes."""
        if len(digit) > 1:
            raise ValueError(f"Expected a single character, got {len(digit)}")
        self.update(_character_map[digit.upper()])


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
