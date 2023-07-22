from textual.reactive import reactive
from textual.widgets import Static


_character_map: dict[str, str] = {}

# in the mappings below, we use underscores to make spaces more visible,
# we will strip them out later
_character_map[
    "0"
] = """
┏━┓
┃ ┃
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

_character_map["D"] = _character_map["0"]

_character_map[
    "E"
] = """
┏━╸
┣━╸
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

_character_map["O"] = _character_map["0"]

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

# here we strip spaces and replace underscores with spaces
_character_map = {k: v.strip() for k, v in _character_map.items()}


def render_digits(digits: str) -> str:
    """Render a string of digits as 7-segment LED-like characters."""
    lines = [""] * 3
    for digit in digits:
        for i, line in enumerate(_character_map[digit].splitlines()):
            lines[i] += line.replace("_", " ")
    return "\n".join(lines)


class LedDisplay(Static):
    """A widget to display characters using 7-segment LED-like format."""

    digits = reactive("", layout=True)

    def __init__(self, initial_value="", **kwargs):
        super().__init__(**kwargs)
        self.digits = initial_value

    def watch_digits(self, digits: str) -> None:
        """Called when the time attribute changes."""
        self.update(render_digits(digits.upper()))
