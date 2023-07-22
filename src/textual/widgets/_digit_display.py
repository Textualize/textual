from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static


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
  ╹
 ╹·
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
    "X"
] = """
╻ ╻
·╋·
╹ ╹
"""

_character_map[
    "Y"
] = """
╻ ╻
·┳·
·╹·
"""

_character_map[
    "Z"
] = """
╺━┓
·▞·
┗━╸
"""


_character_map[
    "."
] = """
··
··
·•
"""


_character_map[
    ","
] = """
··
··
·▞
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
╺━·
╺━·
"""

_character_map[
    "*"
] = """
···
·✱·
···
"""


_character_map[
    "/"
] = """
··╻
·▞·
╹··
"""

_character_map[
    "^"
] = """
·╻·
▝·▘
···
"""


_VIRTUAL_SPACE = "·"

# here we strip spaces and replace virtual spaces with spaces
_character_map = {
    k: v.strip().replace(_VIRTUAL_SPACE, " ") for k, v in _character_map.items()
}


class SingleDigitDisplay(Static):
    digit = reactive(" ", layout=True)

    DEFAULT_CSS = """
        SingleDigitDisplay {
          height: 3;
          min-width: 2;
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


class DigitDisplay(Widget):
    """A widget to display digits and basic arithmetic operators using Unicode blocks."""

    digits = reactive("", layout=True)

    DEFAULT_CSS = """
    DigitDisplay {
        layout: horizontal;
        height: 3;
    }
    """

    def __init__(self, initial_value="", **kwargs):
        super().__init__(**kwargs)
        self._displays = [SingleDigitDisplay(d) for d in initial_value]
        self.digits = initial_value

    def compose(self) -> ComposeResult:
        for widget in self._displays:
            yield widget

    def _add_digit_widget(self, digit: str) -> None:
        new_widget = SingleDigitDisplay(digit)
        self._displays.append(new_widget)
        self.mount(new_widget)

    def watch_digits(self, digits: str) -> None:
        """
        Called when the digits attribute changes.
        Here we update the display widgets to match the input digits.
        """
        diff_digits_len = len(digits) - len(self._displays)

        # Here we add or remove widgets to match the number of digits
        if diff_digits_len > 0:
            start = len(self._displays)
            for i in range(diff_digits_len):
                self._add_digit_widget(digits[start + i])
        elif diff_digits_len < 0:
            for display in self._displays[diff_digits_len:]:
                self._displays.remove(display)
                display.remove()

        # At this point, the number of widgets matches the number of digits, and we can
        # update the contents of the widgets that might need it
        for i, d in enumerate(self.digits):
            if self._displays[i].digit != d:
                self._displays[i].digit = d
