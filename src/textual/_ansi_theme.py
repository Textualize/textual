from __future__ import annotations

from rich.terminal_theme import TerminalTheme


def rgb(red: int, green: int, blue: int) -> tuple[int, int, int]:
    """Define an RGB color.

    This exists mainly so that a VSCode extension can render the colors inline.

    Args:
        red: Red component.
        green: Green component.
        blue: Blue component.

    Returns:
        Color triplet.
    """
    return red, green, blue


MONOKAI = TerminalTheme(
    rgb(12, 12, 12),
    rgb(217, 217, 217),
    [
        rgb(26, 26, 26),
        rgb(244, 0, 95),
        rgb(152, 224, 36),
        rgb(253, 151, 31),
        rgb(157, 101, 255),
        rgb(244, 0, 95),
        rgb(88, 209, 235),
        rgb(196, 197, 181),
        rgb(98, 94, 76),
    ],
    [
        rgb(244, 0, 95),
        rgb(152, 224, 36),
        rgb(224, 213, 97),
        rgb(157, 101, 255),
        rgb(244, 0, 95),
        rgb(88, 209, 235),
        rgb(246, 246, 239),
    ],
)

ALABASTER = TerminalTheme(
    rgb(247, 247, 247),
    rgb(0, 0, 0),
    [
        rgb(0, 0, 0),
        rgb(170, 55, 49),
        rgb(68, 140, 39),
        rgb(203, 144, 0),
        rgb(50, 92, 192),
        rgb(122, 62, 157),
        rgb(0, 131, 178),
        rgb(247, 247, 247),
        rgb(119, 119, 119),
    ],
    [
        rgb(240, 80, 80),
        rgb(96, 203, 0),
        rgb(255, 188, 93),
        rgb(0, 122, 204),
        rgb(230, 76, 230),
        rgb(0, 170, 203),
        rgb(247, 247, 247),
    ],
)

DEFAULT_TERMINAL_THEME = MONOKAI
