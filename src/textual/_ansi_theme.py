from rich.terminal_theme import TerminalTheme

MONOKAI = TerminalTheme(
    (12, 12, 12),
    (217, 217, 217),
    [
        (26, 26, 26),
        (244, 0, 95),
        (152, 224, 36),
        (253, 151, 31),
        (157, 101, 255),
        (244, 0, 95),
        (88, 209, 235),
        (196, 197, 181),
        (98, 94, 76),
    ],
    [
        (244, 0, 95),
        (152, 224, 36),
        (224, 213, 97),
        (157, 101, 255),
        (244, 0, 95),
        (88, 209, 235),
        (246, 246, 239),
    ],
)

ALABASTER = TerminalTheme(
    (247, 247, 247),
    (0, 0, 0),
    [
        (0, 0, 0),
        (170, 55, 49),
        (68, 140, 39),
        (203, 144, 0),
        (50, 92, 192),
        (122, 62, 157),
        (0, 131, 178),
        (247, 247, 247),
        (119, 119, 119),
    ],
    [
        (240, 80, 80),
        (96, 203, 0),
        (255, 188, 93),
        (0, 122, 204),
        (230, 76, 230),
        (0, 170, 203),
        (247, 247, 247),
    ],
)

DEFAULT_TERMINAL_THEME = MONOKAI
