"""
Helpers for detecting Alt-modified key presses on Windows consoles that do not
emit Kitty keyboard protocol sequences.

Windows terminals that only support VT input typically translate `Alt+<key>`
into the two byte sequence ``ESC`` + ``<key>``, which is indistinguishable from
typing Escape followed by the key. The common workaround (used by many TUIs) is
to interpret ``ESC`` followed closely by another printable character as an Alt+key combo.
We perform that translation in the Windows driver before handing the input to :mod:`textual._xterm_parser`.
"""

from __future__ import annotations

from typing import Iterable, List

# ESC-prefixed CSI / SS3 sequences start with these characters; we shouldn't convert them into
# Alt+key combinations because they are almost certainly control sequences from the terminal.
_ESCAPE_PREFIXES = {"[", "O", "P", "]"}


def _decode_control_character(char: str) -> tuple[str, bool]:
    """Convert control codes back to their printable counterparts.

    Args:
        char: Character extracted from the console stream.

    Returns:
        A tuple ``(character, is_ctrl)``.
    """

    code = ord(char)
    if 1 <= code <= 26:
        return chr(code + 96), True
    control_map = {
        0: "@",
        27: "[",
        28: "\\",
        29: "]",
        30: "^",
        31: "_",
        127: "\x7f",
    }
    if code in control_map:
        return control_map[code], True
    return char, False


def _format_alt_sequence(char: str, shift: bool, ctrl: bool) -> str:
    """Build a Kitty keyboard protocol sequence for an Alt-modified character.

    Args:
        char: Base printable character.
        shift: ``True`` if Shift should be reported.
        ctrl: ``True`` if Ctrl should be reported.

    Returns:
        Kitty keyboard protocol sequence.
    """

    modifiers = 1
    if shift:
        modifiers += 1
    modifiers += 2  # Alt
    if ctrl:
        modifiers += 4

    return f"\x1b[{ord(char)};{modifiers}u"


def _synthesize_alt_sequence(char: str, has_trailing_input: bool) -> str | None:
    """Build a fallback Kitty sequence for ESC-prefixed key presses.

    Args:
        char: Character following ``ESC``.
        has_trailing_input: ``True`` if more data follows the pair.

    Returns:
        Kitty keyboard protocol sequence or ``None``.
    """

    if len(char) != 1:
        return None

    base_char, ctrl = _decode_control_character(char)
    if char == "\x1b":
        return None
    if base_char in _ESCAPE_PREFIXES:
        if has_trailing_input:
            return None
        if ctrl:
            return None

    shift = base_char.isalpha() and base_char.isupper()
    return _format_alt_sequence(base_char, shift, ctrl)


def coalesce_alt_sequences(chars: Iterable[str]) -> list[str]:
    """Replace ``ESC`` + ``char`` pairs with Kitty sequences.

    Args:
        chars: Individual characters read from the console.

    Returns:
        A new list of strings where recognized pairs have been replaced with
        Kitty keyboard protocol sequences.
    """

    result: list[str] = []
    chars_list: List[str] = list(chars)
    index = 0
    length = len(chars_list)
    while index < length:
        char = chars_list[index]
        if char == "\x1b" and index + 1 < length:
            next_char = chars_list[index + 1]
            kitty_sequence = _synthesize_alt_sequence(
                next_char, has_trailing_input=index + 2 < length
            )
            if kitty_sequence is not None:
                result.append(kitty_sequence)
                index += 2
                continue
        result.append(char)
        index += 1
    return result
