from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static
from ..geometry import Size


_character_map: dict[str, str] = {}

_VIRTUAL_SPACE = "·"

# in the mappings below, we use a dot instead of spaces to make them more
# visible, we will strip them out later
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
··
╺━
╺━
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


# here we strip spaces and replace virtual spaces with spaces
_character_map = {
    k: v.strip().replace(_VIRTUAL_SPACE, " ") for k, v in _character_map.items()
}


class _SingleDigitDisplay(Static):
    """
    A widget to display a single digit or basic arithmetic symbol using Unicode blocks.
    """

    digit = reactive(" ", layout=True)
    """The digit to display."""

    DEFAULT_CSS = """
    _SingleDigitDisplay {
      height: 3;
      width: 3;
    }
    """

    def __init__(
        self,
        initial_value: str = " ",
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        """
        Create a single digit display widget.

        Example:
            ```py
            class Example(App):
                def compose(self) -> ComposeResult:
                    return _SingleDigitDisplay("1")
        """
        super().__init__(
            expand=expand,
            shrink=shrink,
            markup=markup,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.digit = initial_value

    def validate_digit(self, digit: str) -> str:
        """Sanitize and validate the digit input."""
        if len(digit) > 1:
            raise ValueError(f"Expected a single character, got {len(digit)}")
        digit = digit.upper()
        if digit not in _character_map:
            raise ValueError(f"Unsupported character: {digit}")
        return digit

    def _watch_digit(self, digit: str) -> None:
        """Called when the digit attribute changes and passes validation."""
        content = _character_map[digit.upper()]
        self.update(content)

    def get_content_width(self, container: Size, viewport: Size) -> int:
        return 3

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        return 3


class DigitDisplay(Widget):
    """
    A widget to display digits and basic arithmetic symbols using Unicode blocks.
    """

    digits = reactive("", layout=True)
    """The digits to display."""

    supported_digits = frozenset(_character_map.keys())
    """The digits and characters supported by this widget."""

    DEFAULT_CSS = """
    DigitDisplay {
        layout: horizontal;
        height: 3;
    }
    """

    def __init__(
        self,
        initial_value: str = "",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        """
        Create a Digit Display widget.

        Example:
            ```py
            class Example(App):
                def compose(self) -> ComposeResult:
                    return DigitDisplay("123+456")

        Args:
            initial_value (str, optional): The initial value to display. Defaults to "".
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._displays = [_SingleDigitDisplay(d) for d in initial_value]
        self.digits = initial_value

    def compose(self) -> ComposeResult:
        for widget in self._displays:
            yield widget

    def _watch_digits(self, digits: str) -> None:
        """
        Called when the digits attribute changes.
        Here we update the display widgets to match the input digits.
        """
        # Here we add or remove widgets to match the number of digits
        while len(self._displays) < len(digits):
            self._displays.append(_SingleDigitDisplay(digits[len(self._displays)]))
            self.mount(self._displays[-1])
        while len(self._displays) > len(digits):
            self._displays.pop().remove()

        # At this point, the number of widgets matches the number of digits, and we can
        # update the contents of the widgets that might need it
        for i, d in enumerate(self.digits):
            if self._displays[i].digit != d:
                self._displays[i].digit = d
